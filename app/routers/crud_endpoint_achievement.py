from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.achievement import create_achievement, get_achievement, update_achievement, delete_achievement
from app.schemas.achievement import AchievementCreate, AchievementRead
from app.core.database import get_db

router = APIRouter(
    prefix="/achievements/crud",
    tags=["Achievements"],
    responses={404: {"description": "Achievement not found"}},
)

@router.post("/", response_model=AchievementCreate, summary="Создать достижение")
async def create_achievement_endpoint(achievement_data: AchievementCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новое достижение с переданными данными.
    """
    return await create_achievement(db, achievement_data)

@router.get("/{achievement_id}", response_model=AchievementRead, summary="Получить достижение по ID")
async def get_achievement_endpoint(achievement_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные достижения по его уникальному ID.
    """
    achievement = await get_achievement(db, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return achievement

@router.put("/{achievement_id}", response_model=AchievementRead, summary="Обновить достижение")
async def update_achievement_endpoint(achievement_id: int, updates: AchievementCreate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет данные достижения по его уникальному ID.
    """
    achievement = await update_achievement(db, achievement_id, updates)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return achievement

@router.delete("/{achievement_id}", response_model=dict, summary="Удалить достижение")
async def delete_achievement_endpoint(achievement_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет достижение по его уникальному ID.
    """
    success = await delete_achievement(db, achievement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return {"message": "Achievement deleted successfully"}
