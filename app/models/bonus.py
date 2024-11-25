from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Float
from app.core.database import Base

class PurchasableBonus(Base):
    __tablename__ = "purchasable_bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Название бонуса
    description: Mapped[str] = mapped_column(String, nullable=False)  # Описание
    base_cost: Mapped[int] = mapped_column(Integer, nullable=False)  # Базовая стоимость
    cost_modifier: Mapped[Float] = mapped_column(Float, nullable=False, default=1.2)  # Модификатор удорожания
    max_level: Mapped[int] = mapped_column(Integer, nullable=True)  # Максимальный уровень
    effect: Mapped[str] = mapped_column(String, nullable=False)  # Описание эффекта бонуса

    user_bonuses: Mapped[list["UserBonus"]] = relationship("UserBonus", back_populates="bonus")

class UserBonus(Base):
    __tablename__ = "user_bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bonus_id: Mapped[int] = mapped_column(ForeignKey("purchasable_bonuses.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    level: Mapped[int] = mapped_column(Integer, default=1)  # Текущий уровень бонуса
    total_cost: Mapped[int] = mapped_column(Integer, default=0)  # Общая стоимость бонуса

    bonus: Mapped["PurchasableBonus"] = relationship("PurchasableBonus", back_populates="user_bonuses")
    user: Mapped["User"] = relationship("User", back_populates="user_bonuses")
