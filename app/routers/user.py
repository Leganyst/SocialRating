from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import get_user_by_vk_id
from app.routers.dependencies.auth import get_user_depend
from app.schemas.user import UserBase
from app.core.database import get_db

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/me", summary="Получить данные пользователя")
async def get_user_data(
    user: UserBase = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Возвращает данные пользователя, включая информацию о времени с последнего входа.
    """
    user_data = await get_user_by_vk_id(session, user.vk_id)
    return {"status": "success", "user_data": user_data.model_dump()}
