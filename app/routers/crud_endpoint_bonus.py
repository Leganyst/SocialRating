from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.bonus import (
    create_purchasable_bonus,
    get_purchasable_bonus,
    update_purchasable_bonus,
    delete_purchasable_bonus,
    get_user_bonuses,
    add_or_upgrade_user_bonus,
)
from app.models.bonus import UserBonus
from app.schemas.bonus import BonusCreate, BonusRead, BonusUpdate, UserBonusWithLevelRead
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.schemas.user import UserBase
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(
    prefix="/bonuses",
    tags=["Bonuses"],
    responses={404: {"description": "Bonus not found"}},
)


@router.get("/user", response_model=list[UserBonusWithLevelRead], summary="Получить бонусы пользователя")
async def get_user_bonuses_endpoint(user: UserBase = Depends(get_user_depend), db: AsyncSession = Depends(get_db)):
    """
    Возвращает список бонусов, которыми обладает пользователь, включая их текущий уровень.
    """
    # Загружаем бонусы пользователя с уровнями
    bonuses = await db.execute(
        select(UserBonus).where(UserBonus.user_id == user.id).options(selectinload(UserBonus.bonus))
    )
    bonuses = bonuses.scalars().all()

    # Формируем список объектов с уровнем и данными бонуса
    bonus_list = [
        UserBonusWithLevelRead(
            bonus=BonusRead.model_validate(bonus.bonus),
            level=bonus.level
        )
        for bonus in bonuses if bonus.bonus is not None
    ]

    return bonus_list


# **1. Создание нового покупаемого бонуса**
@router.post("/", response_model=BonusRead, summary="Создать покупаемый бонус")
async def create_bonus_endpoint(bonus_data: BonusCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новый бонус, который может быть приобретен пользователями.
    """
    return await create_purchasable_bonus(db, bonus_data)

# **2. Получение бонуса по ID**
@router.get("/{bonus_id}", response_model=BonusRead, summary="Получить покупаемый бонус по ID")
async def get_bonus_endpoint(bonus_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные покупаемого бонуса по его уникальному ID.
    """
    bonus = await get_purchasable_bonus(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")
    return bonus

# **3. Обновление покупаемого бонуса**
@router.put("/{bonus_id}", response_model=BonusRead, summary="Обновить покупаемый бонус")
async def update_bonus_endpoint(bonus_id: int, updates: BonusUpdate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет данные покупаемого бонуса по его уникальному ID.
    """
    bonus = await update_purchasable_bonus(db, bonus_id, updates)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")
    return bonus

# **4. Удаление покупаемого бонуса**
@router.delete("/{bonus_id}", response_model=dict, summary="Удалить покупаемый бонус")
async def delete_bonus_endpoint(bonus_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет покупаемый бонус по его уникальному ID.
    """
    success = await delete_purchasable_bonus(db, bonus_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bonus not found")
    return {"message": "Bonus deleted successfully"}


# # **6. Добавление или улучшение бонуса пользователя**
# @router.post("/user/{bonus_id}", response_model=dict, summary="Добавить или улучшить бонус пользователя")
# async def add_or_upgrade_bonus_endpoint(bonus_id: int, user: UserBase = Depends(get_user_depend), db: AsyncSession = Depends(get_db)):
#     """
#     Добавляет новый бонус пользователю или улучшает существующий бонус.
#     """
#     user_bonus = await add_or_upgrade_user_bonus(db, user_id=user.id, bonus_id=bonus_id)
#     return {
#         "message": "Bonus added or upgraded successfully",
#         "bonus_id": user_bonus.bonus_id,
#         "new_level": user_bonus.level,
#         "total_cost": user_bonus.total_cost,
#     }
