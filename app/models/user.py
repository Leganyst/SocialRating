from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Уникальный VK ID пользователя
    username: Mapped[str] = mapped_column(String, nullable=True)  # Имя пользователя
    rice: Mapped[int] = mapped_column(Integer, default=0)  # Количество собранного риса
    clicks: Mapped[int] = mapped_column(Integer, default=0)  # Количество кликов
    invited_users: Mapped[int] = mapped_column(Integer, default=0)  # Приглашенные пользователи
    achievements_count: Mapped[int] = mapped_column(Integer, default=0)  # Количество достижений
    social_rating: Mapped[int] = mapped_column(Integer, default=0)  # Рейтинг пользователя
    current_core: Mapped[str] = mapped_column(String, nullable=True)  # Текущий стержень пользователя

    # Привязка к коллективу
    collective_id: Mapped[int] = mapped_column(ForeignKey("collectives.id"), nullable=True)
    collective: Mapped["Collective"] = relationship("Collective", back_populates="members")

    # Достижения пользователя
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="user")

    # Активные бонусы
    user_bonuses: Mapped[list["UserBonus"]] = relationship("UserBonus", back_populates="user")
