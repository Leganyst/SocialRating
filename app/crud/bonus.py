from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bonus import PurchasableBonus, UserBonus
from app.models.user import User
from app.schemas.bonus import BonusCreate, BonusRead, BonusUpdate
from typing import Optional, List


async def create_purchasable_bonus(session: AsyncSession, bonus_data: BonusCreate) -> BonusRead:
    """
    Асинхронное создание нового покупаемого бонуса.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_data: Данные для создания бонуса.
    :return: Сериализованный объект нового бонуса.
    """
    new_bonus = PurchasableBonus(**bonus_data.model_dump())
    session.add(new_bonus)
    await session.commit()
    await session.refresh(new_bonus)
    return BonusRead.model_validate(new_bonus)


async def get_purchasable_bonus(session: AsyncSession, bonus_id: int) -> Optional[BonusRead]:
    """
    Асинхронное получение покупаемого бонуса по ID.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_id: ID бонуса.
    :return: Сериализованный объект бонуса или None.
    """
    result = await session.execute(select(PurchasableBonus).where(PurchasableBonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    return BonusRead.model_validate(bonus) if bonus else None


async def update_purchasable_bonus(session: AsyncSession, bonus_id: int, updates: BonusUpdate) -> Optional[BonusRead]:
    """
    Асинхронное обновление данных покупаемого бонуса.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_id: ID бонуса.
    :param updates: Обновлённые данные бонуса.
    :return: Сериализованный объект обновленного бонуса или None.
    """
    result = await session.execute(select(PurchasableBonus).where(PurchasableBonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if not bonus:
        return None

    # Применяем обновления
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(bonus, key, value)

    await session.commit()
    await session.refresh(bonus)
    return BonusRead.model_validate(bonus)


async def delete_purchasable_bonus(session: AsyncSession, bonus_id: int) -> bool:
    """
    Асинхронное удаление покупаемого бонуса.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_id: ID бонуса.
    :return: True, если бонус был удалён, иначе False.
    """
    result = await session.execute(select(PurchasableBonus).where(PurchasableBonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if not bonus:
        return False

    await session.delete(bonus)
    await session.commit()
    return True


async def get_user_bonuses(session: AsyncSession, user_id: int) -> List[UserBonus]:
    """
    Получает список бонусов, связанных с пользователем.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :return: Список бонусов пользователя.
    """
    result = await session.execute(select(UserBonus).where(UserBonus.user_id == user_id))
    return result.scalars().all()


async def add_or_upgrade_user_bonus(session: AsyncSession, user_id: int, bonus_id: int) -> UserBonus:
    """
    Добавляет бонус пользователю или повышает его уровень.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param bonus_id: ID бонуса.
    :return: Обновлённый бонус пользователя.
    """
    result = await session.execute(
        select(UserBonus).where(UserBonus.user_id == user_id, UserBonus.bonus_id == bonus_id)
    )
    user_bonus = result.scalar_one_or_none()

    # Если бонус уже существует, повышаем его уровень
    if user_bonus:
        # Рассчитываем новую стоимость с учетом модификатора
        purchasable_bonus = await session.execute(select(PurchasableBonus).where(PurchasableBonus.id == bonus_id))
        purchasable_bonus = purchasable_bonus.scalar_one()
        new_cost = int(user_bonus.total_cost + purchasable_bonus.base_cost * (purchasable_bonus.cost_modifier ** user_bonus.level))
        
        user_bonus.level += 1
        user_bonus.total_cost = new_cost
    else:
        # Создаём новый бонус для пользователя
        user_bonus = UserBonus(user_id=user_id, bonus_id=bonus_id, total_cost=0, level=1)

    session.add(user_bonus)
    await session.commit()
    await session.refresh(user_bonus)

    return user_bonus


async def get_all_bonuses(session: AsyncSession) -> List[BonusRead]:
    """
    Получает список всех покупаемых бонусов.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список всех бонусов.
    """
    result = await session.execute(select(PurchasableBonus))
    return [BonusRead.model_validate(bonus) for bonus in result.scalars().all()]