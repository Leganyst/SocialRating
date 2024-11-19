from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.collective import Collective
from schemas.collective import CollectiveCreate, CollectiveRead
from typing import Optional

async def create_collective(db: AsyncSession, collective_data: CollectiveCreate) -> CollectiveRead:
    """Асинхронное создание нового совхоза."""
    new_collective = Collective(**collective_data.dict())
    db.add(new_collective)
    await db.commit()
    await db.refresh(new_collective)
    return CollectiveRead.model_validate(new_collective)

async def get_collective(db: AsyncSession, collective_id: int) -> Optional[CollectiveRead]:
    """Асинхронное получение совхоза по ID."""
    result = await db.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()
    if collective:
        return CollectiveRead.model_validate(collective)
    return None

async def update_collective(db: AsyncSession, collective_id: int, updates: CollectiveCreate) -> Optional[CollectiveRead]:
    """Асинхронное обновление данных совхоза."""
    result = await db.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()
    if not collective:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(collective, key, value)
    await db.commit()
    await db.refresh(collective)
    return CollectiveRead.model_validate(collective)

async def delete_collective(db: AsyncSession, collective_id: int) -> bool:
    """Асинхронное удаление совхоза."""
    result = await db.execute(select(Collective).where(Collective.id == collective_id))
    collective = result.scalar_one_or_none()
    if not collective:
        return False
    await db.delete(collective)
    await db.commit()
    return True
