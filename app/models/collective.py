import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, Integer, String
from app.core.database import Base
from app.models.user import User

class CollectiveType(enum.Enum):
    """Типы коллективов."""
    start = 'Начальный'
    middle = 'Средний'
    big = "Крупный"
    gold = "Золотой"
    diamond = "Алмазный"
    jade = "Нефритовый"

class Collective(Base):
    __tablename__ = 'collectives'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    social_rating: Mapped[int] = mapped_column(Integer, default=0)
    collective_type: Mapped[CollectiveType] = mapped_column(Enum(CollectiveType), nullable=False, default=CollectiveType.start)
    group_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    members: Mapped[list['User']] = relationship('User', back_populates='collective')
