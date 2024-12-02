from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Float
from app.core.database import Base

class PurchasableBonus(Base):
    """
    Покупаемый бонус.
    """
    __tablename__ = "purchasable_bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Название бонуса
    description: Mapped[str] = mapped_column(String, nullable=False)  # Описание бонуса
    base_cost: Mapped[int] = mapped_column(Integer, nullable=False)  # Базовая стоимость
    cost_modifier: Mapped[Float] = mapped_column(Float, nullable=False, default=1.2)  # Модификатор удорожания
    max_level: Mapped[int] = mapped_column(Integer, nullable=True)  # Максимальный уровень
    effect: Mapped[str] = mapped_column(String, nullable=False)  # Описание эффекта бонуса
    image: Mapped[str] = mapped_column(String, nullable=True)  # Ссылка на изображение

    # Конкретные эффекты бонусов
    autocollect_rice_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к автосбору риса (в единицах риса за час)
    autocollect_duration_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Длительность автосбора (в минутах)
    rice_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к ручному сбору риса (%)
    invited_users_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к приглашенным пользователям (множитель)

    user_bonuses: Mapped[list["UserBonus"]] = relationship("UserBonus", back_populates="bonus")


class UserBonus(Base):
    """
    Бонусы, принадлежащие пользователю.
    """
    __tablename__ = "user_bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bonus_id: Mapped[int] = mapped_column(ForeignKey("purchasable_bonuses.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    level: Mapped[int] = mapped_column(Integer, default=1)  # Текущий уровень бонуса
    total_cost: Mapped[int] = mapped_column(Integer, default=0)  # Общая стоимость бонуса

    bonus: Mapped["PurchasableBonus"] = relationship("PurchasableBonus", back_populates="user_bonuses")
    user: Mapped["User"] = relationship("User", back_populates="user_bonuses")
