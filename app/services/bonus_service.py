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
    logger.info(f"Начало нормализации эффекта: '{effect}'")

    # Определяем шаблоны для различных эффектов
    patterns = {
        "autocollect_duration_bonus": r"(врем(я|ени|ем|ям|ям)|длительн.*)\s*автосбора",
        "autocollect_rice_bonus": r"(объ(е|ё)м(у|а|ов|ом)?|автосбор.*рис)",
        "rice_bonus": r"сбор(у|а)?\s*рис",
        "invited_users_bonus": r"привлеч.*\s*друз",
    }

    # Ищем совпадения
    parsed_effects = {}
    logger.info("⟶ Определяем шаблоны для нормализации:")
    for key, pattern in patterns.items():
        logger.info(f"  - Шаблон для {key}: {pattern}")

    # Обработка строки с эффектом
    for key, pattern in patterns.items():
        match = re.search(pattern, effect, re.IGNORECASE)
        if match:
            parsed_effects[key] = match.group(0)
            logger.info(
                f"⟶ Совпадение найдено для {key}:\n"
                f"   - Исходная строка: '{effect}'\n"
                f"   - Распознанный фрагмент: '{match.group(0)}'"
            )
        else:
            logger.info(
                f"⟶ Совпадение для {key} не найдено.\n"
                f"   - Исходная строка: '{effect}'"
            )

    logger.info("⟶ Итоговый результат нормализации эффектов:")
    for key, value in parsed_effects.items():
        logger.info(f"  - {key} → '{value}'")

    if not parsed_effects:
        logger.warning(f"⟶ Эффекты не распознаны для строки: '{effect}'")

    return parsed_effects


async def apply_bonus_to_user(session: AsyncSession, user: User, bonus: PurchasableBonus, level: int) -> None:
    """
    Применяет эффекты бонуса к пользователю. Бонусы остаются неизменными на всех уровнях.
    
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

    logger.info(
        f"Применение бонуса '{bonus.name}' (уровень {level}) для пользователя (ID: {user.id}).\n"
        f"Исходные параметры:\n"
        f"- Время автосбора: {user.autocollect_duration_bonus} мин.\n"
        f"- Объём автосбора: {user.autocollect_rice_bonus} рис/час.\n"
        f"- Ручной сбор риса: {user.rice_bonus}%.\n"
        f"- Привлечение друзей: {user.invited_users_bonus}x."
    )

    for effect in effects:
        effect = effect.strip()
        normalized_effect = normalize_effect(effect)

        for key, value in normalized_effect.items():
            if "%" in effect:
                # Применяем фиксированный процентный бонус
                percentage = int(re.search(r"(\d+)%", effect).group(1))
                previous_value = getattr(user, key)
                changes[key] += percentage
                setattr(user, key, previous_value + percentage)
                logger.info(
                    f"⟶ Эффект '{key}': {percentage}% (фиксировано).\n"
                    f"   Было: {previous_value}, стало: {getattr(user, key)}."
                )
            elif "x" in effect:
                # Применяем фиксированный множитель
                multiplier = int(re.search(r"x(\d+)", effect).group(1))
                previous_value = getattr(user, key)
                changes[key] += multiplier
                setattr(user, key, previous_value + multiplier)
                logger.info(
                    f"⟶ Эффект '{key}': +{multiplier}x (множитель).\n"
                    f"   Было: {previous_value}x, стало: {getattr(user, key)}x."
                )
            elif re.search(r"\d+", effect):  # Прямое число
                amount = int(re.search(r"(\d+)", effect).group(1))
                previous_value = getattr(user, key)
                changes[key] += amount
                setattr(user, key, previous_value + amount)
                logger.info(
                    f"⟶ Эффект '{key}': +{amount} (абсолютное значение).\n"
                    f"   Было: {previous_value}, стало: {getattr(user, key)}."
                )

    # Сохраняем изменения
    session.add(user)
    await session.commit()

    # Финальное логирование изменений
    logger.info(
        f"Применение бонуса '{bonus.name}' завершено. Изменения для пользователя (ID: {user.id}):\n"
        f"⟶ Время автосбора: +{changes['autocollect_duration_bonus']} мин "
        f"(итого: {user.autocollect_duration_bonus} мин).\n"
        f"⟶ Объём автосбора: +{changes['autocollect_rice_bonus']} рис/час "
        f"(итого: {user.autocollect_rice_bonus} рис/час).\n"
        f"⟶ Ручной сбор риса: +{changes['rice_bonus']}% "
        f"(итого: {user.rice_bonus}%).\n"
        f"⟶ Бонус за привлечение друга: +{changes['invited_users_bonus']}x "
        f"(итого: {user.invited_users_bonus}x)."
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
    logger.info(
        f"Пользователь найден: VK ID {user.vk_id} (ID: {user.id}).\n"
        f"Текущие параметры:\n"
        f"- Рис: {user.rice}\n"
        f"- Длительность автосбора: {user.autocollect_duration_bonus} мин.\n"
        f"- Объём автосбора: {user.autocollect_rice_bonus} рис/час.\n"
        f"- Бонус к ручному сбору риса: {user.rice_bonus}%.\n"
        f"- Бонус за друзей: {user.invited_users_bonus}x."
    )

    # Проверяем, был ли бонус уже куплен
    user_bonus = await session.execute(
        select(UserBonus).where(UserBonus.user_id == user_id, UserBonus.bonus_id == bonus_id)
    )
    user_bonus = user_bonus.scalar_one_or_none()
    logger.info(f"Статус бонуса: {'Уже куплен' if user_bonus else 'Ещё не куплен'}.")

    # Рассчитываем стоимость бонуса
    if not user_bonus:
        total_cost = bonus.base_cost
        level = 1
        logger.info(f"Первое приобретение бонуса. Стоимость: {total_cost}. Уровень: {level}.")
    else:
        level = user_bonus.level + 1
        total_cost = int(user_bonus.total_cost + bonus.base_cost * (bonus.cost_modifier ** user_bonus.level))
        logger.info(f"Повышение уровня бонуса. Новый уровень: {level}. Стоимость: {total_cost}.")

    # Проверяем, достаточно ли риса у пользователя
    if user.rice < total_cost:
        logger.error(f"Недостаточно риса для покупки бонуса. Требуется: {total_cost}, доступно: {user.rice}.")
        raise ValueError(f"Недостаточно риса для покупки бонуса: требуется {total_cost}, доступно {user.rice}.")

    # Списываем стоимость бонуса
    logger.info(f"Списание стоимости бонуса. Было риса: {user.rice}.")
    user.rice -= total_cost
    logger.info(f"Остаток риса после списания: {user.rice}.")

    # Обработка "Огородного Тяпки"
    if bonus.name == "Огородный Тяпка":
        if not user_bonus:
            # Первый уровень бонуса
            logger.info(
                f"Применение уникального эффекта 'Огородный Тяпка' (первый уровень):\n"
                f"- Длительность автосбора увеличена на 60 минут.\n"
                f"- Объём автосбора увеличен на 200 рис/час."
            )
            user.autocollect_duration_bonus += 60  # 60 минут
            user.autocollect_rice_bonus += 200  # 200 рис/час
        else:
            # Для последующих уровней
            logger.info(
                f"Применение эффекта 'Огородный Тяпка' (уровень {level}):\n"
                f"- Длительность автосбора увеличена на 10 минут."
            )
            user.autocollect_duration_bonus += 10  # +10 минут
    else:
        # Стандартное применение бонуса
        logger.info(f"Применение стандартного бонуса '{bonus.name}' (уровень {level}).")
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
        logger.info(f"Добавлен новый бонус '{bonus.name}' для пользователя (ID: {user.id}).")
    else:
        logger.info(
            f"Обновление бонуса '{bonus.name}' для пользователя (ID: {user.id}):\n"
            f"- Предыдущий уровень: {user_bonus.level}, новый уровень: {level}.\n"
            f"- Стоимость обновлена с {user_bonus.total_cost} до {total_cost}."
        )
        user_bonus.level = level
        user_bonus.total_cost = total_cost

    # Сохраняем изменения
    await session.commit()
    await session.refresh(user_bonus)

    logger.info(
        f"Бонус '{bonus.name}' успешно сохранён для пользователя (ID: {user.id}):\n"
        f"- Уровень: {user_bonus.level}.\n"
        f"- Общая стоимость: {user_bonus.total_cost}.\n"
        f"Итоговые параметры пользователя:\n"
        f"- Рис: {user.rice}.\n"
        f"- Длительность автосбора: {user.autocollect_duration_bonus} мин.\n"
        f"- Объём автосбора: {user.autocollect_rice_bonus} рис/час."
    )

    return UserBonusRead(
        user_id=user_id,
        bonus_id=bonus_id,
        level=user_bonus.level,
        total_cost=user_bonus.total_cost,
    )
