from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.logger import logger
from app.models.achievement import Achievement, UserAchievement
from app.models.user import User
from datetime import datetime
import re


BONUS_KEYWORDS = {
    "добыча риса": ["добыче риса", "добыча риса", "сбор риса"],
    "время автосбора": ["времени автосбора", "время автосбора"],
    "объём автосбора": ["объёму автосбора", "объём автосбора"],
    "социальный рейтинг": ["соц. рейтинг", "социальный рейтинг"],
    "рис": ["единиц риса", "рис"]
}


async def add_user_achievement(session: AsyncSession, user_id: int, achievement_id: int) -> UserAchievement:
    """
    Добавить достижение пользователю или обновить его прогресс с учётом начисляемых бонусов.
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
    user_achievement = await session.execute(
        select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id
        )
    )
    user_achievement = user_achievement.scalar_one_or_none()

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
    if achievement.bonus:
        logger.info(f"Применение бонусов достижения '{achievement.name}' для пользователя {user_id}: {achievement.bonus}.")
        await apply_achievement_bonus(session, user, achievement.bonus)

    await session.commit()
    await session.refresh(user_achievement)

    logger.info(f"Достижение '{achievement.name}' успешно начислено пользователю {user_id}.")
    return user_achievement


async def apply_achievement_bonus(session: AsyncSession, user: User, bonus_description: str) -> None:
    """
    Применяет бонус достижения к пользователю.

    :param session: Сессия базы данных.
    :param user: Пользователь, к которому применяются бонусы.
    :param bonus_description: Текст описания бонуса достижения.
    """
    logger.info(f"Начало применения бонусов к пользователю (ID: {user.id}): {bonus_description}.")

    # Сохраняем исходные значения для логирования
    initial_values = {
        "social_rating": user.social_rating,
        "autocollect_duration_bonus": user.autocollect_duration_bonus,
        "autocollect_rice_bonus": user.autocollect_rice_bonus,
        "rice_bonus": user.rice_bonus,
        "rice": user.rice,
    }

    # Преобразуем ключевые слова в регулярные выражения
    keyword_patterns = {
        "добыча риса": re.compile(r"(добыч[аеуы]?|сбор[ау]?)\s*рис[ауе]?"),
        "время автосбора": re.compile(r"(врем[яеиау]|длительност[ьи])\s*автосбор[ауе]?"),
        "объём автосбора": re.compile(r"(объ[её]м[ауеи]?|автосбор.*рис[ауе]?)"),
        "социальный рейтинг": re.compile(r"(соц(иальн(ый|ого|ому|ым))?|рейтинг)"),
        "рис": re.compile(r"(\d+)\s*единиц[ауе]?\s*рис[ауе]?"),
    }

    # Разбор бонусов с помощью регулярных выражений
    bonuses = re.findall(r"(\d+)%?\s*([\w\s]+)", bonus_description.lower())

    for match in bonuses:
        value, field = match
        value = int(value)

        # Сопоставляем поле с известными ключевыми словами
        for key, pattern in keyword_patterns.items():
            if pattern.search(field):
                if key == "добыча риса":
                    user.rice_bonus += value
                    logger.info(
                        f"Добавлено {value}% к добыче риса. Было: {initial_values['rice_bonus']}%, стало: {user.rice_bonus}%."
                    )

                elif key == "время автосбора":
                    user.autocollect_duration_bonus += value
                    logger.info(
                        f"Добавлено {value}% к времени автосбора. Было: {initial_values['autocollect_duration_bonus']}%, стало: {user.autocollect_duration_bonus}%."
                    )

                elif key == "объём автосбора":
                    user.autocollect_rice_bonus += value
                    logger.info(
                        f"Добавлено {value}% к объёму автосбора. Было: {initial_values['autocollect_rice_bonus']}%, стало: {user.autocollect_rice_bonus}%."
                    )

                elif key == "социальный рейтинг":
                    user.social_rating += value
                    logger.info(
                        f"Добавлено {value} к социальному рейтингу. Было: {initial_values['social_rating']}, стало: {user.social_rating}."
                    )

                elif key == "рис":
                    user.rice += value
                    logger.info(
                        f"Добавлено {value} риса. Было: {initial_values['rice']}, стало: {user.rice}."
                    )

    # Сохранение изменений
    session.add(user)
    await session.commit()

    # Итоговое логирование изменений
    logger.info(
        f"Применение бонусов завершено для пользователя (ID: {user.id}). Изменения:\n"
        f"- Социальный рейтинг: {initial_values['social_rating']} -> {user.social_rating}\n"
        f"- Длительность автосбора: {initial_values['autocollect_duration_bonus']} -> {user.autocollect_duration_bonus}\n"
        f"- Объём автосбора: {initial_values['autocollect_rice_bonus']} -> {user.autocollect_rice_bonus}\n"
        f"- Бонус к добыче риса: {initial_values['rice_bonus']} -> {user.rice_bonus}\n"
        f"- Общее количество риса: {initial_values['rice']} -> {user.rice}"
    )
