from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserRead
from typing import Optional

def create_user(db: Session, user_data: UserCreate) -> UserRead:
    """Создание нового пользователя."""
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserRead.model_validate(new_user)

def get_user(db: Session, user_id: int) -> Optional[UserRead]:
    """Получение пользователя по ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return UserRead.model_validate(user)
    return None

def update_user(db: Session, user_id: int, updates: UserCreate) -> Optional[UserRead]:
    """Обновление данных пользователя."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)

def delete_user(db: Session, user_id: int) -> bool:
    """Удаление пользователя."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
