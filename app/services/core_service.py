from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import CoreType, User, core_factory, get_all_cores

async def update_user_core(session: AsyncSession, user: User, new_core_type: CoreType) -> bool:
    """
    Обновляет стержень пользователя, добавляя бонусы нового стержня и предыдущих.

    :return: `True`, если стержень успешно обновлён, иначе `False`.
    """
    all_cores = get_all_cores()
    new_core = core_factory(new_core_type)

    # Проверка: можно ли перейти на новый стержень
    if user.social_rating < new_core.required_rating:
        return False  # Недостаточно рейтинга — не обновляем стержень

    # Если текущий стержень уже соответствует новому, ничего не делаем
    if user.current_core == new_core_type.value:
        return False

    # Накопление бонусов от всех предыдущих стержней
    cumulative_bonuses = {"rice_boost": 0, "party_respect": 0, "badge_boost": 0}
    for core in all_cores:
        if user.social_rating >= core.required_rating:
            for bonus, value in core.bonuses.items():
                cumulative_bonuses[bonus] = cumulative_bonuses.get(bonus, 0) + value

        # Останавливаемся на текущем стержне
        if core.type == new_core.type:  # Исправлено: используем type вместо name
            break

    # Обновление пользователя
    user.current_core = new_core_type.value
    user.rice_bonus = int(cumulative_bonuses.get("rice_boost", 0) * 100)  # Конвертируем множитель в проценты
    user.social_rating += cumulative_bonuses.get("party_respect", 0)
    user.invited_users_bonus = cumulative_bonuses.get("badge_boost", 0)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return True


def determine_new_core_type(social_rating: int) -> CoreType:
    """
    Определяет новый стержень на основе социального рейтинга пользователя.

    :param social_rating: Текущий социальный рейтинг пользователя.
    :return: Тип стержня (CoreType).
    """
    all_cores = get_all_cores()

    # Ищем подходящий стержень
    for core in reversed(all_cores):  # Начинаем с самого высокого стержня
        if social_rating >= core.required_rating:
            return core.type

    # Если рейтинг слишком низкий, возвращаем самый базовый стержень
    return CoreType.COPPER
