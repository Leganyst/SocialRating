from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collective import Collective, CollectiveType, collective_factory
from app.models.user import User
from app.crud.collective import get_collective, create_collective
from app.schemas.collective import CollectiveCreate
from app.utils.vk_api import get_group_info
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.schemas.collective import CollectiveCreate
from app.utils.vk_api import get_group_info
from app.crud.collective import get_collective, create_collective
from app.core.logger import logger 


async def get_or_create_collective(session: AsyncSession, group_id: str) -> Collective:
    """
    Проверяет существование коллектива или создает новый.

    :param session: Асинхронная сессия SQLAlchemy.
    :param group_id: ID группы VK.
    :return: Объект коллектива.
    """
    logger.info(f"Проверка существования коллектива с ID группы {group_id}.")

    # Проверяем наличие коллектива с указанным group_id
    result = await session.execute(
        select(Collective).where(Collective.group_id == group_id)
    )
    collective = result.scalar_one_or_none()

    # Если коллектив не найден, создаем новый
    if not collective:
        logger.info(f"Коллектив с ID {group_id} не найден. Создаём новый коллектив.")
        
        group_info = await get_group_info(group_id)  # Предполагается, что эта функция возвращает данные о группе
        collective_data = CollectiveCreate(
            name=group_info.get("name", f"Группа {group_id}"),
            social_rating=0,
            group_id=group_id
        )
        collective = await create_collective(session, collective_data)

        logger.info(f"Создан новый коллектив: {collective.name} (ID: {collective.id}).")
    else:
        logger.info(f"Коллектив с ID {group_id} найден: {collective.name} (ID: {collective.id}).")

    return collective


def determine_new_collective_type(social_rating: int, current_type: CollectiveType) -> CollectiveType:
    """
    Определяет новый тип коллектива на основе социального рейтинга.

    :param social_rating: Текущий социальный рейтинг коллектива.
    :param current_type: Текущий тип коллектива.
    :return: Новый (или тот же) тип коллектива.
    """
    all_types = list(CollectiveType)
    current_index = all_types.index(current_type)

    # Перебираем уровни от большего к меньшему
    for collective_type in reversed(all_types):  # Ограничиваем до текущего уровня включительно
        bonuses = collective_factory(collective_type)
        if social_rating >= bonuses.get("required_rating", 0):
            return collective_type

    return all_types[0]  # Если ничего не подошло, возвращаем самый начальный тип



async def apply_collective_bonuses(session: AsyncSession, user: User, collective: Collective):
    """
    Применяет бонусы совхоза к пользователю, обновляя их с учётом текущего уровня совхоза.
    """
    logger.info(f"Начало применения бонусов совхоза {collective.type.value} для пользователя {user.vk_id}.")

    # Проверяем, был ли обновлён уровень совхоза
    if user.current_collective_type == collective.type:
        logger.info(
            f"Бонусы совхоза {collective.type.value} уже применены для пользователя {user.vk_id}. "
            f"Текущие бонусы: rice_boost={user.collective_rice_boost}, autocollect_bonus={user.collective_autocollect_bonus}."
        )
        return

    # Получаем бонусы текущего уровня совхоза
    bonuses = collective_factory(collective.type)
    new_rice_boost = int(bonuses.get("rice_boost", 0) * 100)
    new_autocollect_bonus = int(bonuses.get("autocollect_bonus", 0) * 100)

    # Логируем изменения
    logger.info(
        f"Применение новых бонусов: rice_boost={new_rice_boost}, autocollect_bonus={new_autocollect_bonus}. "
        f"Старые значения для пользователя {user.vk_id}: rice_boost={user.collective_rice_boost}, "
        f"autocollect_bonus={user.collective_autocollect_bonus}."
    )

    # Обновляем бонусы, добавляя новые к существующим
    user.collective_rice_boost += new_rice_boost
    user.collective_autocollect_bonus += new_autocollect_bonus

    # Обновляем текущий уровень совхоза
    user.current_collective_type = collective.type

    # Сохраняем изменения
    session.add(user)
    await session.commit()

    logger.info(
        f"Обновлённые бонусы для пользователя {user.vk_id}: "
        f"rice_boost={user.collective_rice_boost}, autocollect_bonus={user.collective_autocollect_bonus}, "
        f"current_collective_type={user.current_collective_type}."
    )

        
async def update_collective_type(session: AsyncSession, collective: Collective) -> bool:
    """
    Проверяет и обновляет тип совхоза на основании его социального рейтинга.
    
    :param session: Асинхронная сессия SQLAlchemy.
    :param collective: Объект совхоза.
    :return: `True`, если тип был обновлён, иначе `False`.
    """
    new_type = determine_new_collective_type(collective.social_rating, collective.type)

    if new_type != collective.type:
        logger.info(
            f"Обновление типа совхоза {collective.name}: {collective.type.localized_name()} -> {new_type.localized_name()}."
        )
        collective.type = new_type
        session.add(collective)
        await session.commit()
        return True

    logger.info(f"Тип совхоза {collective.name} остаётся неизменным ({collective.type.localized_name()}).")
    return False



