from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.logger import logger
from app.models.achievement import Achievement, UserAchievement
from app.models.user import User
from datetime import datetime
from typing import Optional


async def add_user_achievement(session: AsyncSession, user_id: int, achievement_id: int) -> UserAchievement:
    """
    Добавить достижение пользователю или обновить его прогресс с учётом начисляемых бонусов.
    
    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param achievement_id: ID достижения.
    :return: ORM-объект UserAchievement.
    """
    logger.info(f"Начало начисления достижения с ID {achievement_id} для пользователя с ID {user_id}.")

    # Получение достижения
    achievement = await session.get(Achievement, achievement_id)
    if not achievement:
        logger.error(f"Достижение с ID {achievement_id} не найдено.")
        raise ValueError(f"Достижение с ID {achievement_id} не найдено.")

    # Получение пользователя
    user = await session.get(User, user_id)
    if not user:
        logger.error(f"Пользователь с ID {user_id} не найден.")
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    # Проверяем, есть ли у пользователя уже это достижение
    result = await session.execute(
        select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id
        )
    )
    user_achievement: Optional[UserAchievement] = result.scalar_one_or_none()

    if user_achievement:
        logger.info(f"Достижение с ID {achievement_id} уже есть у пользователя с ID {user_id}. Обновляем прогресс.")
        user_achievement.last_updated = datetime.utcnow()
        user_achievement.progress += 1
    else:
        # Создаём новое достижение
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            last_updated=datetime.utcnow(),
            is_completed=True
        )
        session.add(user_achievement)
        logger.info(f"Достижение с ID {achievement_id} добавлено пользователю с ID {user_id}.")

    # Применяем бонусы достижения
    logger.info(f"Применение бонусов достижения '{achievement.name}' для пользователя {user_id}.")
    await apply_achievement_bonus(session, user, achievement)

    await session.commit()
    await session.refresh(user_achievement)

    logger.info(f"Достижение '{achievement.name}' успешно начислено пользователю {user_id}.")
    return user_achievement


async def apply_achievement_bonus(session: AsyncSession, user: User, achievement: Achievement) -> None:
    """
    Применяет бонус достижения к пользователю.

    :param session: Сессия базы данных.
    :param user: Пользователь, к которому применяются бонусы.
    :param achievement: Достижение, бонус которого нужно применить.
    """
    logger.info(f"Начало применения бонусов достижения '{achievement.name}' к пользователю (ID: {user.id}).")

    # Сохраняем исходные значения для логирования
    initial_values = {
        "social_rating": user.social_rating,
        "autocollect_duration_bonus": user.autocollect_duration_bonus,
        "autocollect_rice_bonus": user.autocollect_rice_bonus,
        "rice_bonus": user.rice_bonus,
    }

    # Применяем бонусы из достижения
    user.social_rating += achievement.social_rating_bonus
    user.rice_bonus += achievement.rice_production_bonus
    user.autocollect_duration_bonus += achievement.autocollect_duration_bonus

    logger.info(
        f"Бонусы применены к пользователю (ID: {user.id}):\n"
        f"- Социальный рейтинг: {initial_values['social_rating']} -> {user.social_rating}\n"
        f"- Бонус к добыче риса: {initial_values['rice_bonus']} -> {user.rice_bonus}\n"
        f"- Бонус к времени автосбора: {initial_values['autocollect_duration_bonus']} -> {user.autocollect_duration_bonus}"
    )

    # Сохранение изменений
    session.add(user)
    await session.commit()

    logger.info(f"Применение бонусов завершено для пользователя (ID: {user.id}).")
