from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bonus import Bonus
from app.schemas.bonus import BonusCreate, BonusRead, BonusUpdate
from typing import Optional


async def create_bonus(session: AsyncSession, bonus_data: BonusCreate) -> BonusRead:
    """
    Асинхронное создание нового бонуса.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_data: Данные для создания бонуса.
    :return: Сериализованный объект нового бонуса.
    """
    new_bonus = Bonus(**bonus_data.model_dump())
    session.add(new_bonus)
    await session.commit()
    await session.refresh(new_bonus)
    return BonusRead.model_validate(new_bonus)


async def get_bonus(session: AsyncSession, bonus_id: int) -> Optional[BonusRead]:
    """
    Асинхронное получение бонуса по ID.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_id: ID бонуса.
    :return: Сериализованный объект бонуса или None.
    """
    result = await session.execute(select(Bonus).where(Bonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    return BonusRead.model_validate(bonus) if bonus else None


async def update_bonus(session: AsyncSession, bonus_id: int, updates: BonusUpdate) -> Optional[BonusRead]:
    """
    Асинхронное обновление данных бонуса.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_id: ID бонуса.
    :param updates: Обновлённые данные бонуса.
    :return: Сериализованный объект обновленного бонуса или None.
    """
    result = await session.execute(select(Bonus).where(Bonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if not bonus:
        return None

    # Применяем обновления
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(bonus, key, value)

    await session.commit()
    await session.refresh(bonus)
    return BonusRead.model_validate(bonus)


async def delete_bonus(session: AsyncSession, bonus_id: int) -> bool:
    """
    Асинхронное удаление бонуса.

    :param session: Асинхронная сессия SQLAlchemy.
    :param bonus_id: ID бонуса.
    :return: True, если бонус был удалён, иначе False.
    """
    result = await session.execute(select(Bonus).where(Bonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if not bonus:
        return False

    await session.delete(bonus)
    await session.commit()
    return True
