from fastapi import APIRouter, Depends

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
)
async def me(user=Depends(get_current_user)) -> User:
    return user
