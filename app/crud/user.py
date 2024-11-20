from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.collective import Collective
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from typing import Optional

async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
    """Асинхронное создание нового пользователя."""
    new_user = User(**user_data.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Явно указываем пустой список для active_bonuses
    user_data = UserRead.model_validate(
        {**new_user.__dict__, "active_bonuses": []}
    )
    return user_data

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
    result = await db.execute(
        select(User).options(selectinload(User.active_bonuses)).where(User.vk_id == vk_id)
    )
    user = result.scalar_one_or_none()
    if user:
        return UserRead.model_validate(user)
    return None


async def update_user_collective(session: AsyncSession, user: User, collective_id: int) -> User:
    """
    Обновляет привязку пользователя к коллективу.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user: Объект пользователя.
    :param collective_id: ID коллектива.
    :return: Обновленный пользователь.
    """
    user.collective_id = collective_id
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_rice_and_rating(session: AsyncSession, user_id: int, rice_to_deduct: int, rating_to_add: int) -> User:
    """
    Обновляет рис и рейтинг пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param rice_to_deduct: Количество риса для вычитания.
    :param rating_to_add: Количество рейтинга для добавления.
    :return: Обновленный объект пользователя.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.rice -= rice_to_deduct
    user.social_rating += rating_to_add
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_collective_rating(session: AsyncSession, collective_id: int, rating_to_add: int) -> int:
    """
    Обновляет социальный рейтинг совхоза.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_id: ID совхоза.
    :param rating_to_add: Количество рейтинга для добавления.
    :return: Обновленный общий рейтинг совхоза.
    """
    result = await session.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one()
    collective.social_rating += rating_to_add
    session.add(collective)
    await session.commit()
    await session.refresh(collective)
    return collective.social_rating


async def update_user_rice(session: AsyncSession, user_id: int, rice_to_add: int) -> User:
    """
    Обновляет количество риса у пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param rice_to_add: Количество риса для добавления.
    :return: Обновленный объект пользователя.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.rice += rice_to_add
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user