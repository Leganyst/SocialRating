from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bonus import PurchasableBonus, UserBonus
from app.models.user import User
from app.schemas.bonus import UserBonusRead
from app.core.logger import logger
import re


def normalize_effect(effect: str) -> dict:
    """
    Нормализует эффекты бонусов с учётом вариаций слов.

    :param effect: Строка с описанием эффектов.
    :return: Словарь с распознанными эффектами.
    """
    # Определяем шаблоны для различных эффектов
    patterns = {
        "autocollect_duration_bonus": r"(врем(я|ени|ем|ям|ям)|длительн.*)\s*автосбора",
        "autocollect_rice_bonus": r"(объ(е|ё)м(у|а|ов|ом)?|автосбор.*рис)",
        "rice_bonus": r"сбор(у|а)?\s*рис",
        "invited_users_bonus": r"привлеч.*\s*друз",
    }

    # Ищем совпадения
    parsed_effects = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, effect, re.IGNORECASE)
        if match:
            parsed_effects[key] = match.group(0)

    return parsed_effects


async def apply_bonus_to_user(session: AsyncSession, user: User, bonus: PurchasableBonus, level: int) -> None:
    """
    Применяет эффекты бонуса к пользователю.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user: ORM-объект пользователя.
    :param bonus: ORM-объект бонуса.
    :param level: Уровень бонуса.
    """
    effects = bonus.effect.lower().split(",")  # Разделяем эффекты по запятой
    changes = {
        "autocollect_duration_bonus": 0,
        "autocollect_rice_bonus": 0,
        "rice_bonus": 0,
        "invited_users_bonus": 0,
    }

    for effect in effects:
        effect = effect.strip()
        normalized_effect = normalize_effect(effect)

        for key, value in normalized_effect.items():
            if "%" in effect:
                percentage = int(re.search(r"(\d+)%", effect).group(1))
                increment = (getattr(user, key) * percentage // 100) + (percentage * level)
                changes[key] += increment
                setattr(user, key, getattr(user, key) + increment)
            elif "x" in effect:
                multiplier = int(re.search(r"x(\d+)", effect).group(1))
                increment = multiplier * level
                changes[key] += increment
                setattr(user, key, getattr(user, key) + increment)
            elif re.search(r"\d+", effect):  # Прямое число, например "500 рис в час"
                amount = int(re.search(r"(\d+)", effect).group(1))
                increment = amount * level
                changes[key] += increment
                setattr(user, key, getattr(user, key) + increment)

    # Сохраняем изменения
    session.add(user)
    await session.commit()

    # Логирование изменений
    logger.info(
        f"Применён бонус '{bonus.name}' (уровень {level}) к пользователю (ID: {user.id}):\n"
        f"- Время автосбора: +{changes['autocollect_duration_bonus']} мин (в минутах) "
        f"(было: {user.autocollect_duration_bonus - changes['autocollect_duration_bonus']} мин, "
        f"стало: {user.autocollect_duration_bonus} мин).\n"
        f"- Объём автосбора: +{changes['autocollect_rice_bonus']} рис/час (в абсолютных единицах) "
        f"(было: {user.autocollect_rice_bonus - changes['autocollect_rice_bonus']} рис/час, "
        f"стало: {user.autocollect_rice_bonus} рис/час).\n"
        f"- Ручной сбор риса: +{changes['rice_bonus']}% (в процентах) "
        f"(было: {user.rice_bonus - changes['rice_bonus']}%, "
        f"стало: {user.rice_bonus}%).\n"
        f"- Бонус за привлечение друга: +{changes['invited_users_bonus']}x (в коэффициентах) "
        f"(было: {user.invited_users_bonus - changes['invited_users_bonus']}x, "
        f"стало: {user.invited_users_bonus}x).\n"
        f"Итоговые значения для пользователя (ID: {user.id}):\n"
        f"- Время автосбора: {user.autocollect_duration_bonus} мин.\n"
        f"- Объём автосбора: {user.autocollect_rice_bonus} рис/час.\n"
        f"- Ручной сбор риса: {user.rice_bonus}%.\n"
        f"- Привлечение друзей: {user.invited_users_bonus}x."
    )


async def purchase_bonus(session: AsyncSession, user_id: int, bonus_id: int) -> UserBonusRead:
    """
    Покупка бонуса пользователем с обработкой эффектов.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param bonus_id: Идентификатор бонуса.
    :return: Информация о бонусе пользователя.
    """
    logger.info(f"Начало обработки покупки бонуса с ID {bonus_id} для пользователя с ID {user_id}.")

    # Получаем бонус из базы данных
    bonus = await session.execute(select(PurchasableBonus).where(PurchasableBonus.id == bonus_id))
    bonus = bonus.scalar_one_or_none()
    if not bonus:
        logger.error(f"Бонус с ID {bonus_id} не найден.")
        raise ValueError(f"Бонус с ID {bonus_id} не найден.")
    logger.info(f"Получен бонус: {bonus.name} (ID: {bonus.id}).")

    # Получаем пользователя
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.error(f"Пользователь с ID {user_id} не найден.")
        raise ValueError(f"Пользователь с ID {user_id} не найден.")
    logger.info(f"Получен пользователь: {user.vk_id} (ID: {user.id}).")

    # Проверяем, был ли бонус уже куплен
    user_bonus = await session.execute(
        select(UserBonus).where(UserBonus.user_id == user_id, UserBonus.bonus_id == bonus_id)
    )
    user_bonus = user_bonus.scalar_one_or_none()
    logger.info(f"Статус бонуса для пользователя: {'Уже куплен' if user_bonus else 'Ещё не куплен'}.")

    # Рассчитываем стоимость бонуса
    if not user_bonus:
        total_cost = bonus.base_cost
        level = 1
    else:
        level = user_bonus.level + 1
        total_cost = int(user_bonus.total_cost + bonus.base_cost * (bonus.cost_modifier ** user_bonus.level))

    # Проверяем, достаточно ли риса у пользователя
    if user.rice < total_cost:
        logger.error(f"Недостаточно риса для покупки бонуса: требуется {total_cost}, доступно {user.rice}.")
        raise ValueError(f"Недостаточно риса для покупки бонуса: требуется {total_cost}, доступно {user.rice}.")

    # Списываем стоимость бонуса
    user.rice -= total_cost
    logger.info(f"Списано {total_cost} риса с пользователя (ID: {user.id}). Остаток риса: {user.rice}.")

    # Применение бонуса к пользователю
    await apply_bonus_to_user(session, user, bonus, level)

    # Обновляем или добавляем запись о бонусе
    if not user_bonus:
        user_bonus = UserBonus(
            user_id=user_id,
            bonus_id=bonus_id,
            level=level,
            total_cost=total_cost,
        )
        session.add(user_bonus)
        logger.info(f"Добавлен новый бонус '{bonus.name}' для пользователя с ID {user_id}.")
    else:
        user_bonus.level = level
        user_bonus.total_cost = total_cost
        logger.info(f"Обновлён бонус '{bonus.name}' для пользователя с ID {user_id}.")

    # Сохраняем изменения
    await session.commit()
    await session.refresh(user_bonus)

    logger.info(
        f"Бонус успешно сохранён для пользователя с ID {user_id}: "
        f"уровень {user_bonus.level}, общая стоимость {user_bonus.total_cost}."
    )

    return UserBonusRead(
        user_id=user_id,
        bonus_id=bonus_id,
        level=user_bonus.level,
        total_cost=user_bonus.total_cost,
    )
