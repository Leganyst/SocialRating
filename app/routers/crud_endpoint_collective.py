from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.collective import create_collective, get_collective, update_collective, delete_collective
from app.schemas.collective import CollectiveCreate, CollectiveRead
from app.core.database import get_db
from app.models.collective import Collective
from sqlalchemy import select

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

@router.get(
    "/{collective_id}",
    summary="Получение информации о совхозе",
    description="""
        Возвращает информацию о совхозе по его ID.
        Поле `members` принудительно заменяется на пустой список, чтобы избежать лишних загрузок данных.
    """,
    response_model=CollectiveRead,
    responses={
        200: {
            "description": "Информация о совхозе успешно получена.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Collective Name",
                        "social_rating": 150,
                        "group_id": "123456789",
                        "collective_type": "gold",
                        "members": []
                    }
                }
            },
        },
        404: {"description": "Совхоз не найден."},
    },
)
async def get_collective(
    collective_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Ручка для получения информации о совхозе.
    """
    # Получение совхоза по ID
    result = await session.execute(
        select(Collective).where(Collective.id == collective_id)
    )
    collective = result.scalar_one_or_none()

    if not collective:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Совхоз не найден."
        )

    # Принудительная замена `members` на пустой список
    collective_dict = collective.__dict__.copy()
    collective_dict["members"] = []

    # Валидация и возврат
    return CollectiveRead.model_validate(collective_dict)


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
