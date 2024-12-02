from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import load_only
from app.models.achievement import Achievement, AchievementType, UserAchievement
from app.schemas.achievement import AchievementCreate, AchievementRead, AchievementUpdate
from typing import Optional
from sqlalchemy.orm import selectinload


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
    result = await session.execute(
        select(Achievement)
        .options(load_only(
            Achievement.id,
            Achievement.name,
            Achievement.description,
            Achievement.condition,
            Achievement.visual,
            Achievement.is_active,
            Achievement.type,
            Achievement.social_rating_bonus,
            Achievement.rice_production_bonus,
            Achievement.autocollect_duration_bonus
        ))
        .where(Achievement.id == achievement_id)
    )
    achievement = result.scalar_one_or_none()
    if achievement:
        return AchievementRead.model_validate(achievement)
    return None


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


async def get_user_achievement(session: AsyncSession, user_id: int, achievement_id: int) -> Optional[UserAchievement]:
    """
    Получить достижение пользователя.
    """
    result = await session.execute(
        select(UserAchievement).where(
            (UserAchievement.user_id == user_id) & (UserAchievement.achievement_id == achievement_id)
        )
    )
    return result.scalar_one_or_none()


async def can_assign_achievement(session: AsyncSession, user_id: int, achievement: Achievement) -> bool:
    """
    Проверяет, можно ли начислить достижение пользователю.
    """
    user_achievement = await get_user_achievement(session, user_id, achievement.id)

    if not user_achievement:
        return True  # Если пользователь еще не имеет достижения, можно начислить.

    now = datetime.now(timezone.utc)

    if achievement.type == AchievementType.UNIQUE:
        return False  # Уникальное достижение нельзя получить больше одного раза.

    if achievement.type == AchievementType.DAYLY:
        return user_achievement.last_updated.date() < now.date()  # Проверка на ежедневное

    if achievement.type == AchievementType.WEEKLY:
        return user_achievement.last_updated < (now - timedelta(days=7))  # Проверка на еженедельное

    return True


async def get_all_achievements(session: AsyncSession) -> list[Achievement]:
    """
    Возвращает список всех доступных достижений.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список достижений.
    """
    result = await session.execute(select(Achievement))
    return result.scalars().all()


async def get_user_achievements(session: AsyncSession, user_id: int) -> list[UserAchievement]:
    """
    Возвращает список достижений пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Список объектов UserAchievement.
    """
    result = await session.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == user_id)
        .options(selectinload(UserAchievement.achievement))
    )
    return result.scalars().all()