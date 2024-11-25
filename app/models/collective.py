from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Enum
from app.core.database import Base
import enum

class CollectiveType(enum.Enum):
    """Типы колхозов"""
    INITIAL = "Начальный совхоз"
    MEDIUM = "Средний совхоз"
    LARGE = "Крупный совхоз"
    GOLD = "Золотой совхоз"
    DIAMOND = "Алмазный совхоз"
    JADE = "Нефритовый совхоз"

class Collective(Base):
    __tablename__ = "collectives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Название колхоза
    social_rating: Mapped[int] = mapped_column(Integer, default=0)  # Общий рейтинг (сумма рейтингов участников)
    type: Mapped[CollectiveType] = mapped_column(Enum(CollectiveType), default=CollectiveType.INITIAL)  # Тип
    bonus: Mapped[str] = mapped_column(String, nullable=True)  # Бонусы текущего уровня
    group_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Идентификатор группы VK (обязательный)

    # Связь с участниками
    members: Mapped[list["User"]] = relationship("User", back_populates="collective")
