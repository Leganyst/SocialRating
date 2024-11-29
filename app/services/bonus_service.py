from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bonus import PurchasableBonus, UserBonus
from app.models.user import User
from app.schemas.bonus import UserBonusRead
from app.core.logger import logger


async def apply_bonus_to_user(session: AsyncSession, user: User, bonus: PurchasableBonus, level: int) -> None:
    """
    Применяет эффект бонуса к пользователю.
    """
    effect = bonus.effect.lower()

    if "автосбор" in effect:
        if "время" in effect:
            percentage = int(effect.split("%")[0])
            user.autocollect_duration_bonus += percentage * level
        elif "объём" in effect:
            percentage = int(effect.split("%")[0])
            user.autocollect_rice_bonus += percentage * level

    if "сбору рис" in effect:
        percentage = int(effect.split("%")[0])
        user.rice_bonus += percentage * level

    if "привлечение друга" in effect:
        multiplier = int(effect.split("x")[1])
        user.invited_users_bonus += multiplier * level

    await session.commit()


async def purchase_bonus(session: AsyncSession, user_id: int, bonus_id: int) -> UserBonusRead:
    """
    Покупка бонуса пользователем с учётом особенностей бонуса "Тяпка".

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

    # Если бонус "Тяпка"
    if bonus.name == "Огородный Тяпка":
        logger.info("Обработка бонуса 'Огородный Тяпка'.")
        if not user_bonus:
            user.autocollect_duration_bonus += 60  # 60 минут
            user.autocollect_rice_bonus += 200  # 200 рис в час
            logger.info(
                f"Первое приобретение бонуса 'Огородный Тяпка': "
                f"длительность автосбора увеличена на 60 минут, сбор риса увеличен на 200 рис/час."
            )
        else:
            user.autocollect_duration_bonus += 10  # 10 минут
            logger.info(
                f"Повышение уровня бонуса 'Огородный Тяпка': длительность автосбора увеличена на 10 минут."
            )
    else:
        logger.info(f"Обработка стандартного бонуса: {bonus.name}.")

    # Обновляем или добавляем бонус
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
    session.add(user)
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
