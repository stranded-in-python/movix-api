from fastapi import APIRouter, Depends, status

from models.models import User
from services.users import get_current_user

router = APIRouter()


@router.get(
    "/me",
    response_model=User,
    summary="Личные настройки",
    description="Получить личные настройки",
    response_description="Идентификатор, список прав, статус сервиса авторизации",
    tags=['Пользователь'],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user."}
    },
)
async def me(user=Depends(get_current_user)) -> User:
    return user
