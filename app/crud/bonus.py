from sqlalchemy.orm import Session
from models.bonus import Bonus
from schemas.bonus import BonusCreate, BonusRead
from typing import Optional

def create_bonus(db: Session, bonus_data: BonusCreate) -> BonusRead:
    """Создание нового бонуса."""
    new_bonus = Bonus(**bonus_data.dict())
    db.add(new_bonus)
    db.commit()
    db.refresh(new_bonus)
    return BonusRead.model_validate(new_bonus)

def get_bonus(db: Session, bonus_id: int) -> Optional[BonusRead]:
    """Получение бонуса по ID."""
    bonus = db.query(Bonus).filter(Bonus.id == bonus_id).first()
    if bonus:
        return BonusRead.model_validate(bonus)
    return None

def update_bonus(db: Session, bonus_id: int, updates: BonusCreate) -> Optional[BonusRead]:
    """Обновление данных бонуса."""
    bonus = db.query(Bonus).filter(Bonus.id == bonus_id).first()
    if not bonus:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(bonus, key, value)
    db.commit()
    db.refresh(bonus)
    return BonusRead.model_validate(bonus)

def delete_bonus(db: Session, bonus_id: int) -> bool:
    """Удаление бонуса."""
    bonus = db.query(Bonus).filter(Bonus.id == bonus_id).first()
    if not bonus:
        return False
    db.delete(bonus)
    db.commit()
    return True
