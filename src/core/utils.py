from typing import Any

import jwt
import orjson
from pydantic import SecretStr

JWT_ALGORITHM = 'HS256'


def orjson_dumps(v, *, default=None):
    return orjson.dumps(v, default=default).decode()


def _get_secret_value(secret: SecretStr) -> str:
    if isinstance(secret, str):
        return secret

    return secret.get_secret_value()


async def read_token(
    token: str,
    secret: SecretStr,
    audience: str,
    algorithms: list[str] = [JWT_ALGORITHM],
) -> dict[str, Any]:
    return jwt.decode(
        token, _get_secret_value(secret), audience=audience, algorithms=algorithms
    )
