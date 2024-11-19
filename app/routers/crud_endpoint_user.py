from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import create_user, get_user, update_user, delete_user
from app.schemas.user import UserCreate, UserRead
from app.core.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "User not found"}},
)

@router.post("/", response_model=UserRead, summary="Создать пользователя")
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового пользователя с переданными данными.
    """
    return await create_user(db, user_data)

@router.get("/{user_id}", response_model=UserRead, summary="Получить пользователя по ID")
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные пользователя по его уникальному ID.
    """
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserRead, summary="Обновить пользователя")
async def update_user_endpoint(user_id: int, updates: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет данные пользователя по его уникальному ID.
    """
    user = await update_user(db, user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", response_model=dict, summary="Удалить пользователя")
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет пользователя по его уникальному ID.
    """
    success = await delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
