from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import handle_authentication
from app.routers.dependencies.auth import get_query_params
from app.schemas.user import UserBase, UserRead
from app.schemas.collective import CollectiveBase

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get(
    "/",
    summary="Аутентификация и проверка пользователя и коллектива",
    description="""
        Выполняет аутентификацию пользователя и привязку к коллективу.
        
        Возможные сценарии:
        - Если пользователь заходит впервые, он создается.
        - Если пользователь заходит впервые и указывает группу, она проверяется или создается.
        - Если пользователь возвращается, проверяется его привязка к группе и обновляется при необходимости.
    """,
    response_model=dict,
    responses={
        200: {
            "description": "Успешная аутентификация.",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 1,
                            "vk_id": "123456789",
                            "username": "example_user",
                            "rice": 100,
                            "clicks": 50,
                            "invited_users": 5,
                            "achievements_count": 2,
                            "social_rating": 10,
                            "current_core": "Железный стержень",
                            "collective_id": 1
                        },
                        "collective": {
                            "id": 1,
                            "name": "Примерный коллектив",
                            "social_rating": 150,
                            "type": "Начальный совхоз",
                            "bonus": "Скорость работы +10%"
                        }
                    }
                }
            },
        },
        400: {
            "description": "Ошибка: отсутствует параметр `vk_user_id` в токене.",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing vk_user_id in token"}
                }
            },
        },
        401: {
            "description": "Ошибка проверки подлинности токена.",
            "content": {
                "application/json": {
                    "example": {"detail": "Token validation failed"}
                }
            },
        },
    },
)
@router.get(
    "/",
    summary="Аутентификация и проверка пользователя и коллектива",
    response_model=dict
)
async def authenticate_user(
    query_params: dict = Depends(get_query_params),
    session: AsyncSession = Depends(get_db),
):
    """
    Выполняет аутентификацию пользователя и проверку коллектива.
    """
    vk_id = query_params.get("vk_user_id")
    group_id = query_params.get("vk_group_id")

    if not vk_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing vk_user_id in token")

    result = await handle_authentication(session, vk_id, group_id)
    return result
