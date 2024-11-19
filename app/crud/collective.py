from sqlalchemy.orm import Session
from models.collective import Collective
from schemas.collective import CollectiveCreate, CollectiveRead
from typing import Optional

def create_collective(db: Session, collective_data: CollectiveCreate) -> CollectiveRead:
    """Создание нового совхоза."""
    new_collective = Collective(**collective_data.dict())
    db.add(new_collective)
    db.commit()
    db.refresh(new_collective)
    return CollectiveRead.model_validate(new_collective)

def get_collective(db: Session, collective_id: int) -> Optional[CollectiveRead]:
    """Получение совхоза по ID."""
    collective = db.query(Collective).filter(Collective.id == collective_id).first()
    if collective:
        return CollectiveRead.model_validate(collective)
    return None

def update_collective(db: Session, collective_id: int, updates: CollectiveCreate) -> Optional[CollectiveRead]:
    """Обновление данных совхоза."""
    collective = db.query(Collective).filter(Collective.id == collective_id).first()
    if not collective:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(collective, key, value)
    db.commit()
    db.refresh(collective)
    return CollectiveRead.model_validate(collective)

def delete_collective(db: Session, collective_id: int) -> bool:
    """Удаление совхоза."""
    collective = db.query(Collective).filter(Collective.id == collective_id).first()
    if not collective:
        return False
    db.delete(collective)
    db.commit()
    return True
