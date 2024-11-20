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

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import handle_authentication
from app.routers.dependencies.auth import get_query_params

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get(
    "/",
    summary="Аутентификация и проверка пользователя и коллектива",
    description="""
        Выполняет аутентификацию пользователя и привязку к коллективу.
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
                            "social_rating": 10,
                            "active_bonuses": [],
                            "collective_id": 1
                        },
                        "collective": {
                            "id": 1,
                            "name": "Example Collective",
                            "social_rating": 100,
                            "group_id": "987654321",
                            "members": []
                        }
                    }
                }
            },
        },
        400: {"description": "В токене отсутствует параметр `vk_group_id`."},
        401: {"description": "Токен не прошел проверку подлинности."},
    },
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

    result = await handle_authentication(session, vk_id, int(group_id) if group_id else None)
    return result
