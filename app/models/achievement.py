from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, Enum, DateTime
from app.core.database import Base
from datetime import datetime, timezone

import enum

class AchievementType(enum.Enum):
    UNIQUE = "Уникальное"
    DAYLY = "Ежедневное"
    WEEKLY = "Еженедельное"

class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Название достижения
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Описание достижения
    condition: Mapped[str] = mapped_column(Text, nullable=False)  # Условие получения
    bonus: Mapped[str] = mapped_column(String, nullable=False)  # Получаемый бонус
    visual: Mapped[str] = mapped_column(String, nullable=True)  # Визуализация
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Активно ли достижение
    type: Mapped[AchievementType] = mapped_column(Enum(AchievementType), nullable=False)  # Тип достижения

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement"
    )


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)  # Завершено ли достижение
    progress: Mapped[int] = mapped_column(Integer, default=0)  # Текущий прогресс
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))  # Последнее обновление

    user: Mapped["User"] = relationship("User", back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")
