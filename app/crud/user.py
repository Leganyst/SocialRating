from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from typing import Optional

async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
    """Асинхронное создание нового пользователя."""
    new_user = User(**user_data.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserRead.model_validate(new_user)

async def get_user(db: AsyncSession, user_id: int) -> Optional[UserRead]:
    """Асинхронное получение пользователя по ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        return UserRead.model_validate(user)
    return None

async def update_user(db: AsyncSession, user_id: int, updates: UserCreate) -> Optional[UserRead]:
    """Асинхронное обновление данных пользователя."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Асинхронное удаление пользователя."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True


async def get_user_by_vk_id(db: AsyncSession, vk_id: str) -> Optional[UserRead]:
    """Асинхронное извлечение юзера по его вк ид"""
    result = await db.execute(select(User).where(User.vk_id == vk_id))
    user = result.scalar_one_or_none()
    if user:
        return UserRead.model_validate(user)
    return None
