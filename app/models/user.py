from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, ForeignKey
from app.core.database import Base
from sqlalchemy.dialects.postgresql import JSON
import enum

from app.models.collective import CollectiveType


class CoreType(enum.Enum):
    COPPER = "COPPER"  # Медный стержень
    IRON = "IRON"      # Железный стержень
    GOLD = "GOLD"      # Золотой стержень
    DIAMOND = "DIAMOND"  # Алмазный стержень
    JADE = "JADE"      # Нефритовый стержень

    def localized_name(self) -> str:
        """
        Возвращает локализованное название стержня.
        """
        mapping = {
            "COPPER": "Медный стержень",
            "IRON": "Железный стержень",
            "GOLD": "Золотой стержень",
            "DIAMOND": "Алмазный стержень",
            "JADE": "Нефритовый стержень",
        }
        return mapping[self.value]
    
class Core:
    def __init__(self, type: CoreType, description: str, required_rating: int, bonuses: dict):
        self.type = type
        self.description = description
        self.required_rating = required_rating
        self.bonuses = bonuses
        
        
def core_factory(core_type: CoreType) -> Core:
    cores = {
        CoreType.COPPER: Core(CoreType.COPPER, "Начальный стержень", 10, {"rice_boost": -0.1}),
        CoreType.IRON: Core(CoreType.IRON, "Продолжение пути", 1000, {"rice_boost": 0.2}),
        CoreType.GOLD: Core(CoreType.GOLD, "Уважение партии", 10000, {"party_respect": 10}),
        CoreType.DIAMOND: Core(CoreType.DIAMOND, "Уровень Мао", 100000, {"rice_boost": 0.3}),
        CoreType.JADE: Core(CoreType.JADE, "Главный в партии", 1000000, {"badge_boost": 0.5}),
    }
    return cores[core_type]


def get_all_cores() -> list[Core]:
    return [
        Core(CoreType.COPPER, "Начальный стержень", 10, {"rice_boost": -0.1}),
        Core(CoreType.IRON, "Продолжение пути", 1000, {"rice_boost": 0.2}),
        Core(CoreType.GOLD, "Уважение партии", 10000, {"party_respect": 10}),
        Core(CoreType.DIAMOND, "Уровень Мао", 100000, {"rice_boost": 0.3}),
        Core(CoreType.JADE, "Главный в партии", 1000000, {"badge_boost": 0.5}),
    ]

class UserRoles(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Уникальный VK ID пользователя
    username: Mapped[str] = mapped_column(String, nullable=True)  # Имя пользователя
    is_invited: Mapped[bool] = mapped_column(Boolean, default=False)  # Приглашен ли пользователь
    role: Mapped[UserRoles] = mapped_column(Enum(UserRoles), default=UserRoles.user)  # Роль пользователя
    current_collective_type: Mapped[str] = mapped_column(String, nullable=True)

    rice: Mapped[int] = mapped_column(Integer, default=0)  # Количество собранного риса
    social_rating: Mapped[int] = mapped_column(Integer, default=0)  # Рейтинг пользователя
    clicks: Mapped[int] = mapped_column(Integer, default=0)  # Количество кликов
    invited_users: Mapped[int] = mapped_column(Integer, default=0)  # Приглашенные пользователи
    achievements_count: Mapped[int] = mapped_column(Integer, default=0)  # Количество достижений
    last_entry: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)  # Последний вход
    current_core: Mapped[CoreType] = mapped_column(Enum(CoreType), nullable=False, default=CoreType.COPPER)  # Текущий стержень пользователя

    # Бонусы риса
    autocollect_rice_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к автосбору риса (в единицах риса за час)
    autocollect_duration_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Длительность автосбора (в минутах)
    rice_bonus: Mapped[int] = mapped_column(Integer, default=0)  #  Бонус к ручному сбору риса (%)
    invited_users_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к приглашенным пользователям (множитель)

    # Новое поле для хранения всех бонусов
    # cumulative_bonuses: Mapped[dict] = mapped_column(JSON, default=dict)  # Хранение всех накопленных бонусов в формате JSON

    # Привязка к коллективу
    collective_id: Mapped[int] = mapped_column(ForeignKey("collectives.id"), nullable=True)
    start_collective_id: Mapped[int] = mapped_column(ForeignKey("collectives.id"), nullable=True)
    current_collective_type: Mapped[CollectiveType] = mapped_column(Enum(CollectiveType), nullable=True, default=None)
    collective_rice_boost: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к сбору риса (%)
    collective_autocollect_bonus: Mapped[int] = mapped_column(Integer, default=0)  # Бонус к автосбору риса (в единицах риса за час)

    collective: Mapped["Collective"] = relationship(
        "Collective",
        back_populates="members",
        foreign_keys="User.collective_id",  # Указываем, что связь с `members` идет через `collective_id`
    )
    start_collective: Mapped["Collective"] = relationship(
        "Collective",
        foreign_keys="User.start_collective_id",  # Указываем, что связь идет через `start_collective_id`
    )

    # Достижения пользователя
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="user")

    # Активные бонусы
    user_bonuses: Mapped[list["UserBonus"]] = relationship("UserBonus", back_populates="user")