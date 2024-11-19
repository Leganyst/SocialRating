from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.collective import create_collective, get_collective, update_collective, delete_collective
from app.schemas.collective import CollectiveCreate, CollectiveRead
from app.core.database import get_db

router = APIRouter(
    prefix="/collectives",
    tags=["Collectives"],
    responses={404: {"description": "Collective not found"}},
)

@router.post("/", response_model=CollectiveRead, summary="Создать совхоз")
async def create_collective_endpoint(collective_data: CollectiveCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новый совхоз с переданными данными.
    """
    return await create_collective(db, collective_data)

@router.get("/{collective_id}", response_model=CollectiveRead, summary="Получить совхоз по ID")
async def get_collective_endpoint(collective_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные совхоза по его уникальному ID.
    """
    collective = await get_collective(db, collective_id)
    if not collective:
        raise HTTPException(status_code=404, detail="Collective not found")
    return collective

@router.put("/{collective_id}", response_model=CollectiveRead, summary="Обновить совхоз")
async def update_collective_endpoint(collective_id: int, updates: CollectiveCreate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет данные совхоза по его уникальному ID.
    """
    collective = await update_collective(db, collective_id, updates)
    if not collective:
        raise HTTPException(status_code=404, detail="Collective not found")
    return collective

@router.delete("/{collective_id}", response_model=dict, summary="Удалить совхоз")
async def delete_collective_endpoint(collective_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет совхоз по его уникальному ID.
    """
    success = await delete_collective(db, collective_id)
    if not success:
        raise HTTPException(status_code=404, detail="Collective not found")
    return {"message": "Collective deleted successfully"}
