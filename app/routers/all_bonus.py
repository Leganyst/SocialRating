from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.bonus import get_all_bonuses

router = APIRouter(prefix="/bonuses", tags=["Bonuses"])

@router.get(
    "/all/bonuses",
    summary="Список всех бонусов",
    description="Получить список всех покупаемых бонусов.",
    response_model=dict,
    responses={
        200: {
            "description": "Список всех бонусов.",
            "content": {
                "application/json": {
                    "example": {
                        "bonuses": [
                            {
                                "id": 1,
                                "name": "Бонус 1",
                                "description": "Описание бонуса 1",
                                "base_cost": 100,
                                "cost_modifier": 1.2,
                                "max_level": 5,
                                "effect": "Эффект бонуса 1",
                                "image": "https://example.com/image1.jpg"
                            },
                            {
                                "id": 2,
                                "name": "Бонус 2",
                                "description": "Описание бонуса 2",
                                "base_cost": 200,
                                "cost_modifier": 1.3,
                                "max_level": 3,
                                "effect": "Эффект бонуса 2",
                                "image": "https://example.com/image2.jpg"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_all_bonuses_endpoint(
    session: AsyncSession = Depends(get_db),
):
    """
    Ручка для получения списка всех бонусов.
    """
    bonuses = await get_all_bonuses(session)
    return {"bonuses": bonuses}
