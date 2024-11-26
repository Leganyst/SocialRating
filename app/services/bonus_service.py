from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bonus import PurchasableBonus, UserBonus
from app.models.user import User
from app.schemas.bonus import UserBonusRead


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
    # Получаем бонус из базы данных
    bonus = await session.execute(select(PurchasableBonus).where(PurchasableBonus.id == bonus_id))
    bonus = bonus.scalar_one_or_none()
    if not bonus:
        raise ValueError(f"Бонус с ID {bonus_id} не найден.")

    # Получаем пользователя
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    # Проверяем, был ли бонус уже куплен
    user_bonus = await session.execute(
        select(UserBonus).where(UserBonus.user_id == user_id, UserBonus.bonus_id == bonus_id)
    )
    user_bonus = user_bonus.scalar_one_or_none()

    # Если бонус "Тяпка" покупается впервые
    if bonus.name == "Огородный Тяпка":
        if not user_bonus:
            # Первый автосбор: 1 час, 200 рис в час
            user.autocollect_duration_bonus += 60  # 60 минут
            user.autocollect_rice_bonus += 200  # 200 рис в час
            level = 1
            total_cost = bonus.base_cost
        else:
            # Увеличиваем автосбор на 10 минут
            user.autocollect_duration_bonus += 10
            level = user_bonus.level + 1
            total_cost = int(user_bonus.total_cost + bonus.base_cost * (bonus.cost_modifier ** user_bonus.level))

        # Обновляем или добавляем бонус
        if not user_bonus:
            user_bonus = UserBonus(
                user_id=user_id,
                bonus_id=bonus_id,
                level=level,
                total_cost=total_cost,
            )
            session.add(user_bonus)
        else:
            user_bonus.level = level
            user_bonus.total_cost = total_cost

    else:
        # Обрабатываем стандартный бонус
        if not user_bonus:
            level = 1
            total_cost = bonus.base_cost
            user_bonus = UserBonus(
                user_id=user_id,
                bonus_id=bonus_id,
                level=level,
                total_cost=total_cost,
            )
            session.add(user_bonus)
        else:
            level = user_bonus.level + 1
            total_cost = int(user_bonus.total_cost + bonus.base_cost * (bonus.cost_modifier ** user_bonus.level))
            user_bonus.level = level
            user_bonus.total_cost = total_cost

    # Сохраняем изменения
    session.add(user)
    await session.commit()
    await session.refresh(user_bonus)

    return UserBonusRead(
        user_id=user_id,
        bonus_id=bonus_id,
        level=user_bonus.level,
        total_cost=user_bonus.total_cost,
    )
