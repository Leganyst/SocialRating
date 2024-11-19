from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.bonus import create_bonus, get_bonus, update_bonus, delete_bonus
from app.schemas.bonus import BonusCreate, BonusRead
from app.core.database import get_db

router = APIRouter(
    prefix="/bonuses",
    tags=["Bonuses"],
    responses={404: {"description": "Bonus not found"}},
)

@router.post("/", response_model=BonusRead, summary="Создать бонус")
async def create_bonus_endpoint(bonus_data: BonusCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новый бонус с переданными данными.
    """
    return await create_bonus(db, bonus_data)

@router.get("/{bonus_id}", response_model=BonusRead, summary="Получить бонус по ID")
async def get_bonus_endpoint(bonus_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные бонуса по его уникальному ID.
    """
    bonus = await get_bonus(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")
    return bonus

@router.put("/{bonus_id}", response_model=BonusRead, summary="Обновить бонус")
async def update_bonus_endpoint(bonus_id: int, updates: BonusCreate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет данные бонуса по его уникальному ID.
    """
    bonus = await update_bonus(db, bonus_id, updates)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")
    return bonus

@router.delete("/{bonus_id}", response_model=dict, summary="Удалить бонус")
async def delete_bonus_endpoint(bonus_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет бонус по его уникальному ID.
    """
    success = await delete_bonus(db, bonus_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bonus not found")
    return {"message": "Bonus deleted successfully"}
