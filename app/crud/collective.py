from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.collective import Collective
from app.schemas.collective import CollectiveCreate, CollectiveRead, CollectiveUpdate
from typing import Optional
from fastapi import HTTPException

async def create_collective(session: AsyncSession, collective_data: CollectiveCreate) -> CollectiveRead:
    """
    Асинхронное создание нового коллектива.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_data: Данные для создания коллектива.
    :return: Данные созданного коллектива.
    """
    new_collective = Collective(**collective_data.model_dump())
    session.add(new_collective)
    await session.commit()
    await session.refresh(new_collective)

    # Возвращаем только данные самого коллектива
    return CollectiveRead.model_validate(new_collective)


async def get_collective(session: AsyncSession, collective_id: int) -> Optional[CollectiveRead]:
    """
    Асинхронное получение коллектива по ID.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_id: ID коллектива.
    :return: Данные коллектива или None, если он не найден.
    """
    result = await session.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()
    return CollectiveRead.model_validate(collective) if collective else None


async def update_collective(session: AsyncSession, collective_id: int, updates: CollectiveUpdate) -> Optional[CollectiveRead]:
    """
    Асинхронное обновление данных коллектива.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_id: ID коллектива.
    :param updates: Обновленные данные коллектива.
    :return: Обновленные данные коллектива или None, если он не найден.
    """
    result = await session.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()
    if not collective:
        return None

    # Применяем обновления
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(collective, key, value)

    await session.commit()
    await session.refresh(collective)
    return CollectiveRead.model_validate(collective)


async def delete_collective(session: AsyncSession, collective_id: int) -> bool:
    """
    Асинхронное удаление коллектива.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_id: ID коллектива.
    :return: True, если удаление успешно, иначе False.
    """
    result = await session.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()
    if not collective:
        return False

    await session.delete(collective)
    await session.commit()
    return True


async def get_collective_members(session: AsyncSession, collective_id: int, limit: int = 10) -> list:
    """
    Получение списка участников коллектива с ограничением.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_id: ID коллектива.
    :param limit: Максимальное количество участников для загрузки.
    :return: Список участников.
    """
    from app.models.user import User  # Импорт модели User
    result = await session.execute(
        select(User).where(User.collective_id == collective_id).limit(limit)
    )
    return result.scalars().all()


async def update_collective_rating(session: AsyncSession, collective_id: int, rating_to_add: int) -> int:
    """
    Обновляет социальный рейтинг коллектива.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective_id: ID коллектива.
    :param rating_to_add: Количество рейтинга для добавления.
    :return: Обновленный общий рейтинг коллектива.
    """
    # Получаем коллектив по ID
    result = await session.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()

    if not collective:
        raise HTTPException(
            status_code=404,
            detail=f"Collective with ID {collective_id} not found."
        )

    # Увеличиваем социальный рейтинг
    collective.social_rating += rating_to_add

    # Сохраняем изменения
    session.add(collective)
    await session.commit()
    await session.refresh(collective)

    return collective.social_rating
