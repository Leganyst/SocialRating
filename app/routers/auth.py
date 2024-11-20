from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db 
from app.services.auth_service import handle_authentication
from app.crud.collective import create_collective, get_collective
from app.crud.user import create_user
from app.schemas.collective import CollectiveCreate
from app.schemas.user import UserCreate, UserRead
from app.routers.dependencies.auth import get_query_params, get_user_depend

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get(
    "/",
    summary="Аутентификация и проверка пользователя и коллектива",
    description="""
        Выполняет аутентификацию пользователя и привязку к коллективу.
        - Если пользователь заходит с новой группой, создается или обновляется коллектив.
        - Возвращаются данные пользователя и текущего коллектива (если есть).
    """,
    response_model=UserRead,
    responses={
        200: {
            "description": "Успешная аутентификация.",
            "content": {
                "application/json": {
                    "example": UserRead.example()
                }
            },
        },
        400: {"description": "В токене отсутствует параметр `vk_group_id`."},
        401: {"description": "Токен не прошел проверку подлинности."},
    },
)
async def authenticate_user(
    user: UserRead = Depends(get_user_depend),
    query_params: dict = Depends(get_query_params),
    session: AsyncSession = Depends(get_db),
):
    """
    Выполняет аутентификацию пользователя и проверку коллектива.
    """
    
    group_id = query_params.get("vk_group_id")
    if not group_id:
        if not user:
            result = await create_user(session, UserCreate(
                username=None,
                vk_id=query_params.get("vk_user_id"),
                rice=0,
                clicks=0,
                invited_users=0,
                achievements_count=0,
                social_rating=0,
                collective_id=None
            ))
            return result
        return user
    result = await handle_authentication(session, query_params, int(group_id))
    return result