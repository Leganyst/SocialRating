from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class CoreType(Enum):
    COPPER = "Медный стержень"
    IRON = "Железный стержень"
    GOLD = "Золотой стержень"
    DIAMOND = "Алмазный стержень"
    JADE = "Нефритовый стержень"

class Core:
    def __init__(self, name: str, description: str, required_rating: int, bonuses: dict):
        self.name = name
        self.description = description
        self.required_rating = required_rating
        self.bonuses = bonuses  # Словарь бонусов

def core_factory(core_type: CoreType) -> Core:
    cores = {
        CoreType.COPPER: Core("Медный стержень", "Начальный стержень", 10, {"rice_boost": -0.1}),
        CoreType.IRON: Core("Железный стержень", "Продолжение пути", 1000, {"rice_boost": 0.2}),
        CoreType.GOLD: Core("Золотой стержень", "Уважение партии", 10000, {"party_respect": 10}),
        CoreType.DIAMOND: Core("Алмазный стержень", "Уровень Мао", 100000, {"rice_boost": 0.3}),
        CoreType.JADE: Core("Нефритовый стержень", "Главный в партии", 1000000, {"badge_boost": 0.5}),
    }
    return cores[core_type]

def get_all_cores() -> list[Core]:
    """Получить список всех стержней в порядке их прогрессии."""
    return [
        core_factory(CoreType.COPPER),
        core_factory(CoreType.IRON),
        core_factory(CoreType.GOLD),
        core_factory(CoreType.DIAMOND),
        core_factory(CoreType.JADE),
    ]




async def update_user_core(session: AsyncSession, user: User, new_core_type: CoreType):
    """
    Обновляет стержень пользователя, добавляя бонусы нового стержня и предыдущих.
    """
    all_cores = get_all_cores()
    new_core = core_factory(new_core_type)

    # Проверка: можно ли перейти на новый стержень
    if user.social_rating < new_core.required_rating:
        raise ValueError("Недостаточно социального рейтинга для перехода на этот стержень.")

    # Если текущий стержень уже соответствует новому, ничего не делаем
    if user.current_core == new_core_type.value:
        return

    # Накопление бонусов от всех предыдущих стержней
    cumulative_bonuses = {"rice_boost": 0, "party_respect": 0, "badge_boost": 0}
    for core in all_cores:
        if user.social_rating >= core.required_rating:
            for bonus, value in core.bonuses.items():
                cumulative_bonuses[bonus] = cumulative_bonuses.get(bonus, 0) + value

        # Останавливаемся на текущем стержне
        if core.name == new_core.name:
            break

    # Обновление пользователя
    user.current_core = new_core_type.value
    user.rice_bonus = int(cumulative_bonuses.get("rice_boost", 0) * 100)  # Конвертируем множитель в проценты
    user.social_rating += cumulative_bonuses.get("party_respect", 0)
    user.invited_users_bonus = cumulative_bonuses.get("badge_boost", 0)

    session.add(user)
    await session.commit()
    await session.refresh(user)
