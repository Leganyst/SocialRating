from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.models.user import User
from app.crud.bonus import get_all_bonuses, get_purchasable_bonus, add_or_upgrade_user_bonus

router = APIRouter(
    prefix="/bonuses",
    tags=["Bonuses"],
)


@router.get(
    "/list",
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


@router.post(
    "/buy/{bonus_id}",
    summary="Купить бонус",
    description="""
        Позволяет пользователю купить бонус за рис.
        - Если бонус уже куплен, его уровень повышается.
        - Стоимость покупки рассчитывается с учетом текущего уровня и модификатора стоимости.
    """,
    response_model=dict,
)
async def buy_bonus(
    bonus_id: int,
    user: User = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Ручка для покупки бонуса.
    """
    # Получаем покупаемый бонус
    bonus = await get_purchasable_bonus(session, bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бонус не найден.")

    # Проверяем наличие бонуса у пользователя
    user_bonus = await add_or_upgrade_user_bonus(session, user.id, bonus_id)

    # Рассчитываем стоимость покупки
    current_level = user_bonus.level
    cost = int(bonus.base_cost * (bonus.cost_modifier ** (current_level - 1)))

    if user.rice < cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно риса для покупки бонуса.")

    # Списываем рис у пользователя
    user.rice -= cost
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
        "status": "success",
        "bonus_id": bonus_id,
        "new_level": user_bonus.level,
        "total_cost": user_bonus.total_cost,
        "remaining_rice": user.rice,
    }


