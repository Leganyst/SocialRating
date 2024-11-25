from enum import Enum

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
        self.bonuses = bonuses

def core_factory(core_type: CoreType) -> Core:
    cores = {
        CoreType.COPPER: Core("Медный стержень", "Начальный стержень", 10, {"rice_boost": -0.1}),
        CoreType.IRON: Core("Железный стержень", "Продолжение пути", 1000, {"rice_boost": 0.2}),
        CoreType.GOLD: Core("Золотой стержень", "Уважение партии", 10000, {"party_respect": 10}),
        CoreType.DIAMOND: Core("Алмазный стержень", "Уровень Мао", 100000, {"rice_boost": 0.3}),
        CoreType.JADE: Core("Нефритовый стержень", "Главный в партии", 1000000, {"badge_boost": 0.5}),
    }
    return cores[core_type]
