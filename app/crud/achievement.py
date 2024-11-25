from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreate, AchievementRead, AchievementUpdate
from typing import Optional


async def create_achievement(session: AsyncSession, achievement_data: AchievementCreate) -> AchievementRead:
    """
    Асинхронное создание нового достижения.

    :param session: Асинхронная сессия SQLAlchemy.
    :param achievement_data: Данные для создания достижения.
    :return: Сериализованный объект нового достижения.
    """
    new_achievement = Achievement(**achievement_data.model_dump())
    session.add(new_achievement)
    await session.commit()
    await session.refresh(new_achievement)
    return AchievementRead.model_validate(new_achievement)


async def get_achievement(session: AsyncSession, achievement_id: int) -> Optional[AchievementRead]:
    """
    Асинхронное получение достижения по ID.

    :param session: Асинхронная сессия SQLAlchemy.
    :param achievement_id: ID достижения.
    :return: Сериализованный объект достижения или None.
    """
    result = await session.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    return AchievementRead.model_validate(achievement) if achievement else None


async def update_achievement(session: AsyncSession, achievement_id: int, updates: AchievementUpdate) -> Optional[AchievementRead]:
    """
    Асинхронное обновление данных достижения.

    :param session: Асинхронная сессия SQLAlchemy.
    :param achievement_id: ID достижения.
    :param updates: Обновлённые данные достижения.
    :return: Сериализованный объект обновленного достижения или None.
    """
    result = await session.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    if not achievement:
        return None

    # Применяем обновления
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(achievement, key, value)

    await session.commit()
    await session.refresh(achievement)
    return AchievementRead.model_validate(achievement)


async def delete_achievement(session: AsyncSession, achievement_id: int) -> bool:
    """
    Асинхронное удаление достижения.

    :param session: Асинхронная сессия SQLAlchemy.
    :param achievement_id: ID достижения.
    :return: True, если достижение было удалено, иначе False.
    """
    result = await session.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    if not achievement:
        return False

    await session.delete(achievement)
    await session.commit()
    return True
