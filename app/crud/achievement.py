from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreate, AchievementRead
from typing import Optional

async def create_achievement(db: AsyncSession, achievement_data: AchievementCreate) -> AchievementRead:
    """Асинхронное создание нового достижения."""
    new_achievement = Achievement(**achievement_data.dict())
    db.add(new_achievement)
    await db.commit()
    await db.refresh(new_achievement)
    return AchievementRead.model_validate(new_achievement)

async def get_achievement(db: AsyncSession, achievement_id: int) -> Optional[AchievementRead]:
    """Асинхронное получение достижения по ID."""
    result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    if achievement:
        return AchievementRead.model_validate(achievement)
    return None

async def update_achievement(db: AsyncSession, achievement_id: int, updates: AchievementCreate) -> Optional[AchievementRead]:
    """Асинхронное обновление данных достижения."""
    result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    if not achievement:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(achievement, key, value)
    await db.commit()
    await db.refresh(achievement)
    return AchievementRead.model_validate(achievement)

async def delete_achievement(db: AsyncSession, achievement_id: int) -> bool:
    """Асинхронное удаление достижения."""
    result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalar_one_or_none()
    if not achievement:
        return False
    await db.delete(achievement)
    await db.commit()
    return True
