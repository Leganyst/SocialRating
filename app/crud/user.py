from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from typing import Optional


async def create_user(session: AsyncSession, user_data: UserCreate) -> UserRead:
    """
    Асинхронное создание нового пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_data: Данные для создания пользователя.
    :return: Сериализованный объект нового пользователя.
    """
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Возвращаем только основные данные пользователя
    return UserRead.model_validate(new_user)


async def get_user(session: AsyncSession, user_id: int) -> Optional[UserRead]:
    """
    Асинхронное получение пользователя по ID.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :return: Сериализованный объект пользователя или None.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return UserRead.model_validate(user) if user else None


async def update_user(session: AsyncSession, user_id: int, updates: UserUpdate) -> Optional[UserRead]:
    """
    Асинхронное обновление данных пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param updates: Обновленные данные пользователя.
    :return: Сериализованный объект обновленного пользователя или None.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    """
    Асинхронное удаление пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :return: True, если пользователь был удален, иначе False.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False

    await session.delete(user)
    await session.commit()
    return True


async def get_user_by_vk_id(session: AsyncSession, vk_id: str) -> Optional[UserRead]:
    """
    Асинхронное извлечение пользователя по VK ID.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :return: Сериализованный объект пользователя или None.
    """
    result = await session.execute(select(User).where(User.vk_id == vk_id))
    user = result.scalar_one_or_none()
    return UserRead.model_validate(user) if user else None


async def update_user_rice_and_rating(session: AsyncSession, user_id: int, rice_to_deduct: int, rating_to_add: int) -> Optional[UserRead]:
    """
    Обновляет количество риса и социальный рейтинг пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param rice_to_deduct: Количество риса для вычитания.
    :param rating_to_add: Количество рейтинга для добавления.
    :return: Сериализованный объект обновленного пользователя или None.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    user.rice -= rice_to_deduct
    user.social_rating += rating_to_add
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


async def update_user_rice(session: AsyncSession, user_id: int, rice_to_add: int) -> Optional[UserRead]:
    """
    Обновляет количество риса у пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param rice_to_add: Количество риса для добавления.
    :return: Сериализованный объект обновленного пользователя или None.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    user.rice += rice_to_add
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


async def update_user_collective(session: AsyncSession, vk_id: str, collective_id: int) -> User:
    """
    Обновляет привязку пользователя к коллективу.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user: Объект пользователя, чья привязка обновляется.
    :param collective_id: ID нового коллектива.
    :return: Обновленный объект пользователя.
    """
    user = await session.execute(select(User).where(User.vk_id == vk_id))
    user = user.scalar_one_or_none()
    
    # Проверяем, нужно ли обновлять привязку
    if user.collective_id == collective_id:
        return user

    # Обновляем привязку пользователя к коллективу
    user.collective_id = collective_id

    # Сохраняем изменения
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user