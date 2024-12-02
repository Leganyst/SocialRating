from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Integer, String, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base
import enum


class CollectiveType(enum.Enum):
    INITIAL = "INITIAL"  # Начальный совхоз
    MEDIUM = "MEDIUM"    # Средний совхоз
    LARGE = "LARGE"      # Крупный совхоз
    GOLD = "GOLD"        # Золотой совхоз
    DIAMOND = "DIAMOND"  # Алмазный совхоз
    JADE = "JADE"        # Нефритовый совхоз

    def localized_name(self) -> str:
        """
        Возвращает локализованное название совхоза.
        """
        mapping = {
            "INITIAL": "Начальный совхоз",
            "MEDIUM": "Средний совхоз",
            "LARGE": "Крупный совхоз",
            "GOLD": "Золотой совхоз",
            "DIAMOND": "Алмазный совхоз",
            "JADE": "Нефритовый совхоз",
        }
        return mapping[self.value]
    
class CollectiveLevel:
    def __init__(self, name: str, description: str, required_rating: int, bonuses: dict):
        self.name = name
        self.description = description
        self.required_rating = required_rating
        self.bonuses = bonuses

def collective_factory(collective_type: CollectiveType) -> dict:
    bonuses = {
        CollectiveType.INITIAL: {"rice_boost": 0.05, "autocollect_bonus": 0, "required_rating": 0},
        CollectiveType.MEDIUM: {"rice_boost": 0.1, "autocollect_bonus": 0, "required_rating": 100_000},
        CollectiveType.LARGE: {"rice_boost": 0.2, "autocollect_bonus": 0.05, "required_rating": 1_000_000},
        CollectiveType.GOLD: {"rice_boost": 0.25, "autocollect_bonus": 0.1, "required_rating": 10_000_000},
        CollectiveType.DIAMOND: {"rice_boost": 0.3, "autocollect_bonus": 0.15, "required_rating": 100_000_000},
        CollectiveType.JADE: {"rice_boost": 0.4, "autocollect_bonus": 0.2, "required_rating": 1_000_000_000},
    }
    return bonuses.get(collective_type, {})

class Collective(Base):
    __tablename__ = "collectives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Название совхоза
    social_rating: Mapped[int] = mapped_column(BigInteger, default=0)  # Общий рейтинг (сумма рейтингов участников)
    type: Mapped[CollectiveType] = mapped_column(Enum(CollectiveType), nullable=False, default=CollectiveType.INITIAL)  # Тип совхоза
    group_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Идентификатор группы VK (обязательный)

    # Указываем, какой внешний ключ использовать для связи с пользователями
    members: Mapped[list["User"]] = relationship(
        "User",
        back_populates="collective",
        foreign_keys="User.collective_id",  # Указываем, что связь с `members` идет через `collective_id`
    )