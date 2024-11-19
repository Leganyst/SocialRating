from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.bonus import Bonus
from app.schemas.bonus import BonusCreate, BonusRead
from typing import Optional

async def create_bonus(db: AsyncSession, bonus_data: BonusCreate) -> BonusRead:
    """Асинхронное создание нового бонуса."""
    new_bonus = Bonus(**bonus_data.model_dump())
    db.add(new_bonus)
    await db.commit()
    await db.refresh(new_bonus)
    return BonusRead.model_validate(new_bonus)

async def get_bonus(db: AsyncSession, bonus_id: int) -> Optional[BonusRead]:
    """Асинхронное получение бонуса по ID."""
    result = await db.execute(select(Bonus).where(Bonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if bonus:
        return BonusRead.model_validate(bonus)
    return None

async def update_bonus(db: AsyncSession, bonus_id: int, updates: BonusCreate) -> Optional[BonusRead]:
    """Асинхронное обновление данных бонуса."""
    result = await db.execute(select(Bonus).where(Bonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if not bonus:
        return None
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(bonus, key, value)
    await db.commit()
    await db.refresh(bonus)
    return BonusRead.model_validate(bonus)

async def delete_bonus(db: AsyncSession, bonus_id: int) -> bool:
    """Асинхронное удаление бонуса."""
    result = await db.execute(select(Bonus).where(Bonus.id == bonus_id))
    bonus = result.scalar_one_or_none()
    if not bonus:
        return False
    await db.delete(bonus)
    await db.commit()
    return True
