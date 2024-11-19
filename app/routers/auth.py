from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db 
from app.crud.collective import create_collective, get_collective
from app.crud.user import create_user
from app.schemas.collective import CollectiveCreate
from app.schemas.user import UserCreate, UserRead
from app.routers.dependencies.auth import get_query_params, get_user_depend

router = APIRouter()

@router.get(
    "/auth",
    response_model=UserRead, 
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
    description=(
        "Эндпоинт для аутентификации пользователя через VK. "
        "Если пользователь не существует в базе данных, создается новый."
    ),
    responses={
        200: {
            "description": "Успешная аутентификация",
            "content": {
                "application/json": {
                    "example": UserRead.example()
                }
            }
        },
        401: {
            "description": "Неверный токен аутентификации",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        400: {
            "description": "Некорректный запрос",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            }
        }
    }
)
async def auth_user(user: UserRead = Depends(get_user_depend), session: AsyncSession = Depends(get_db),
                    user_data: dict = Depends(get_query_params)):
    """
    Аутентифицирует пользователя на основе предоставленного токена VK.

    - **user**: Объект пользователя, полученный из зависимости `get_user_depend`.
    - **session**: Сессия базы данных.

    Если пользователь не найден в базе данных, создается новый пользователь.
    Можно использовать как GetMe ручку, для получения обновленной информации о пользователе.
    """
    if user_data.get("vk_group_id"):
        collective = await get_collective(session, user_data.get("vk_group_id"))
        if not collective: 
            pass
            # collective_data = await get_vk_inform()
            # await create_collective(session, CollectiveCreate(
            #    vk_id=collective_data.get("vk_group_id"),
            #    name=collective_data.get("name"),
            
            # ))
    
    if not user:
        user = await create_user(session, UserCreate(
            vk_id=user_data.get("vk_user_id"),
            username=None,
            rice=0,
            clicks=0,
            invited_users=0,
            achievements_count=0,
            social_rating=0,
            collective_id=user_data.get("vk_group_id"),
            active_bonuses=[]
        ))
    return user
