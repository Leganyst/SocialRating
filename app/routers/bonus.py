from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.models.user import User
from app.crud.bonus import get_all_bonuses, get_purchasable_bonus, add_or_upgrade_user_bonus
from app.schemas.bonus import BonusRead, UserBonusRead
from app.schemas.user import UserRead
from app.services.bonus_service import purchase_bonus

router = APIRouter(
    prefix="/bonuses",
    tags=["Bonuses"],
)


@router.post("/{bonus_id}/purchase", response_model=UserBonusRead, summary="Покупка бонуса пользователем")
async def purchase_bonus_endpoint(
    bonus_id: int, user: UserRead = Depends(get_user_depend), db: AsyncSession = Depends(get_db)
):
    """
    Покупка бонуса пользователем.
    """
    try:
        user_bonus = await purchase_bonus(db, user_id=user.user_id, bonus_id=bonus_id)
        return user_bonus
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
