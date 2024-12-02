from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.bonus import get_purchasable_bonus, get_user_bonus
from app.crud.user import get_user, get_user_raw
from app.models.bonus import PurchasableBonus, UserBonus
from app.models.user import User
from app.schemas.bonus import UserBonusRead
from app.core.logger import logger
import re

def calculate_bonus_cost(bonus: PurchasableBonus, user_bonus: Optional[UserBonus]) -> Tuple[int, int]:
    """
    Рассчитывает стоимость бонуса и уровень для пользователя.

    :param bonus: ORM-объект бонуса.
    :param user_bonus: Информация о бонусе пользователя (может быть None).
    :return: Кортеж (total_cost, level).
    """
    if not user_bonus:
        # Если бонус ещё не был куплен
        total_cost = bonus.base_cost
        level = 1
        logger.info(f"Первое приобретение бонуса. Стоимость: {total_cost}. Уровень: {level}.")
    else:
        # Если бонус уже был куплен, рассчитываем следующий уровень и стоимость
        level = user_bonus.level + 1
        total_cost = int(user_bonus.total_cost + bonus.base_cost * (bonus.cost_modifier ** user_bonus.level))
        logger.info(f"Повышение уровня бонуса. Новый уровень: {level}. Стоимость: {total_cost}.")
    return total_cost, level



def apply_bonus_effects(user: User, bonus: PurchasableBonus) -> None:
    logger.info(f"Применение эффектов бонуса '{bonus.name}'.")
    user.autocollect_rice_bonus += bonus.autocollect_rice_bonus
    user.autocollect_duration_bonus += bonus.autocollect_duration_bonus
    user.rice_bonus += bonus.rice_bonus
    user.invited_users_bonus += bonus.invited_users_bonus
    logger.info(
        f"Эффекты применены:\n"
        f"- Длительность автосбора: {user.autocollect_duration_bonus} мин.\n"
        f"- Объём автосбора: {user.autocollect_rice_bonus} рис/час.\n"
        f"- Бонус к ручному сбору риса: {user.rice_bonus}%.\n"
        f"- Бонус за друзей: {user.invited_users_bonus}x."
    )


async def update_user_bonus(
    session: AsyncSession, user_bonus: Optional[UserBonus], user_id: int, bonus_id: int, total_cost: int, level: int
) -> UserBonus:
    if not user_bonus:
        user_bonus = UserBonus(
            user_id=user_id,
            bonus_id=bonus_id,
            level=level,
            total_cost=total_cost,
        )
        session.add(user_bonus)
        logger.info(f"Добавлен новый бонус для пользователя ID {user_id}.")
    else:
        logger.info(
            f"Обновление бонуса для пользователя ID {user_id}:\n"
            f"- Предыдущий уровень: {user_bonus.level}, новый уровень: {level}.\n"
            f"- Стоимость обновлена с {user_bonus.total_cost} до {total_cost}."
        )
        user_bonus.level = level
        user_bonus.total_cost = total_cost
    return user_bonus


def process_ogorod_tiapa(user: User, user_bonus: Optional[UserBonus], level: int) -> None:
    """
    Обрабатывает бонус "Огородная Тяпка" для пользователя.
    
    :param user: ORM-объект пользователя.
    :param user_bonus: Информация о бонусе пользователя (если бонус уже был куплен).
    :param level: Уровень бонуса.
    """
    if not user_bonus:
        # Первая покупка
        logger.info(
            "Применение уникального эффекта 'Огородная Тяпка' (первый уровень):\n"
            "- Длительность автосбора увеличена на 60 минут.\n"
            "- Объём автосбора увеличен на 200 рис/час."
        )
        user.autocollect_duration_bonus += 60  # +60 минут
        user.autocollect_rice_bonus += 200    # +200 рис/час
    else:
        # Последующие уровни
        logger.info(
            f"Применение эффекта 'Огородная Тяпка' (уровень {level}):\n"
            "- Длительность автосбора увеличена на 10 минут."
        )
        user.autocollect_duration_bonus += 10  # +10 минут


async def purchase_bonus(session: AsyncSession, user_id: int, bonus_id: int) -> UserBonusRead:
    logger.info(f"Начало обработки покупки бонуса с ID {bonus_id} для пользователя с ID {user_id}.")

    # Получение бонуса и пользователя
    bonus = await get_purchasable_bonus(session, bonus_id)
    if not bonus:
        logger.error(f"Бонус с ID {bonus_id} не найден.")
        raise ValueError(f"Бонус с ID {bonus_id} не найден.")

    user = await get_user_raw(session, user_id)
    if not user:
        logger.error(f"Пользователь с ID {user_id} не найден.")
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    # Получение и проверка предыдущих покупок бонуса
    user_bonus = await get_user_bonus(session, user_id, bonus_id)

    # Расчёт стоимости и уровня
    total_cost, level = calculate_bonus_cost(bonus, user_bonus)

    # Проверка баланса пользователя
    if user.rice < total_cost:
        logger.error(f"Недостаточно риса для покупки бонуса. Требуется: {total_cost}, доступно: {user.rice}.")
        raise ValueError(f"Недостаточно риса для покупки бонуса: требуется {total_cost}, доступно {user.rice}.")
    user.rice -= total_cost
    logger.info(f"Списание стоимости бонуса. Остаток риса: {user.rice}.")

    # Особая обработка "Огородной Тяпки"
    if bonus.name.lower() == "огородный тяпка":
        process_ogorod_tiapa(user, user_bonus, level)
    else:
        # Применение стандартных эффектов
        apply_bonus_effects(user, bonus)

    # Обновление данных о бонусе
    user_bonus = await update_user_bonus(session, user_bonus, user_id, bonus_id, total_cost, level)

    # Сохранение изменений
    session.add(user)
    await session.commit()
    await session.refresh(user_bonus)

    logger.info(
        f"Бонус '{bonus.name}' успешно сохранён для пользователя (ID: {user.id}):\n"
        f"- Уровень: {user_bonus.level}.\n"
        f"- Общая стоимость: {user_bonus.total_cost}.\n"
        f"- Рис: {user.rice}."
    )

    return UserBonusRead(
        user_id=user_id,
        bonus_id=bonus_id,
        level=user_bonus.level,
        total_cost=user_bonus.total_cost,
    )
