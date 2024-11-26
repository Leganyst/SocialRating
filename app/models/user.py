from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Уникальный VK ID пользователя
    username: Mapped[str] = mapped_column(String, nullable=True)  # Имя пользователя
    is_invited: Mapped[bool] = mapped_column(Boolean, default=False)  # Приглашен ли пользователь
    
    rice: Mapped[int] = mapped_column(Integer, default=0)  # Количество собранного риса
    social_rating: Mapped[int] = mapped_column(Integer, default=0)  # Рейтинг пользователя
    clicks: Mapped[int] = mapped_column(Integer, default=0)  # Количество кликов
    invited_users: Mapped[int] = mapped_column(Integer, default=0)  # Приглашенные пользователи
    achievements_count: Mapped[int] = mapped_column(Integer, default=0)  # Количество достижений
    last_entry: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)  # Последний вход
    current_core: Mapped[str] = mapped_column(String, nullable=True)  # Текущий стержень пользователя
    
    # Бонусы риса
    autocollect_rice_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к австосбору риса (%)
    autocollect_duration_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Длительность автосбора (в минутах)
    rice_bonus: Mapped[int] = mapped_column(Integer, default=0)  #  Бонус к ручному сбору риса (%)
    invited_users_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к приглашенным пользователям (множитель)

    # Привязка к коллективу
    collective_id: Mapped[int] = mapped_column(ForeignKey("collectives.id"), nullable=True)
    start_collective_id: Mapped[int] = mapped_column(ForeignKey("collectives.id"), nullable=True)
    collective: Mapped["Collective"] = relationship("Collective", back_populates="members")


    # Достижения пользователя
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="user")

    # Активные бонусы
    user_bonuses: Mapped[list["UserBonus"]] = relationship("UserBonus", back_populates="user")
