import uuid
from typing import Annotated

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.utils import read_token as jwt_read_token
from models import models

oauth_scheme = OAuth2PasswordBearer(tokenUrl='token')


class TokenReadingError(Exception):
    ...


class NotAuthorizedError(Exception):
    ...


async def get_user_rights(user: models.User, token: str) -> models.User:
    url = str(settings.auth_user_rights_endpoint).replace('user_id', str(user.id))
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Request-Id': f'movix-api:{uuid.uuid4()}',
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        access_rights = response.json()
        if not isinstance(access_rights, list):
            return user
        user.access_rights = (
            [right.get("name") for right in access_rights] if access_rights else []
        )

    return user


async def read_token(token: str) -> models.User:
    try:
        contents = await jwt_read_token(
            token, settings.access_token_secret, audience=settings.access_token_audience
        )
    except jwt.exceptions.PyJWTError as e:
        raise TokenReadingError(str(e))

    user_id = contents.get('sub')
    if not user_id:
        raise TokenReadingError('Ivalid token: no user id found')

    return models.User(uuid=user_id)


async def get_current_user(token: Annotated[str, Depends(oauth_scheme)]) -> models.User:
    try:
        user = await read_token(token)
    except TokenReadingError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        user = await get_user_rights(user, token)
    except httpx.ConnectError:
        user.auth_timeout = True
    except NotAuthorizedError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user
