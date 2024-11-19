from sqlalchemy.orm import Session
from models.achievement import Achievement
from schemas.achievement import AchievementCreate, AchievementRead
from typing import Optional

def create_achievement(db: Session, achievement_data: AchievementCreate) -> AchievementRead:
    """Создание нового достижения."""
    new_achievement = Achievement(**achievement_data.dict())
    db.add(new_achievement)
    db.commit()
    db.refresh(new_achievement)
    return AchievementRead.model_validate(new_achievement)

def get_achievement(db: Session, achievement_id: int) -> Optional[AchievementRead]:
    """Получение достижения по ID."""
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if achievement:
        return AchievementRead.model_validate(achievement)
    return None

def update_achievement(db: Session, achievement_id: int, updates: AchievementCreate) -> Optional[AchievementRead]:
    """Обновление данных достижения."""
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(achievement, key, value)
    db.commit()
    db.refresh(achievement)
    return AchievementRead.model_validate(achievement)

def delete_achievement(db: Session, achievement_id: int) -> bool:
    """Удаление достижения."""
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        return False
    db.delete(achievement)
    db.commit()
    return True
