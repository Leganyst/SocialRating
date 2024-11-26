from app.crud.collective import update_collective_level
from app.schemas.collective import CollectiveRead
from app.services.collective_service import apply_collective_bonuses
from app.services.core_service import determine_new_core_type, update_user_core
from app.services.other import serialize_orm_object
from app.services.user_service import create_or_update_user
from app.core.logger import logger
from app.models.collective import Collective
from app.schemas.user import UserRead
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select

async def handle_authentication(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Выполняет аутентификацию, обработку пользователя и коллектива, а также проверяет стержень пользователя
    и применяет бонусы совхоза.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK.
    :return: Словарь с данными пользователя и коллектива.
    """
    logger.info(f"Начата аутентификация пользователя {vk_id}")

    # Создаем или обновляем пользователя и коллектив
    result = await create_or_update_user(session, vk_id, group_id)
    user = result["user"]

    # Проверяем стержень пользователя
    try:
        new_core_type = determine_new_core_type(user.social_rating)
        await update_user_core(session, user, new_core_type)
        logger.info(f"Стержень пользователя {user.vk_id} обновлён до {new_core_type.value}")
    except ValueError as e:
        logger.warning(f"Стержень пользователя {user.vk_id} не обновлён: {str(e)}")

    # Применяем бонусы совхоза
    collective_data = {}
    if user.collective_id:
        try:
            collective = await session.get(Collective, user.collective_id)
            updated_collective = await update_collective_level(session, collective)
            await apply_collective_bonuses(session, updated_collective)
            logger.info(f"Бонусы совхоза {collective.name} применены")
            collective_data = await serialize_orm_object(collective, CollectiveRead)
        except Exception as e:
            logger.error(f"Ошибка при обновлении совхоза: {str(e)}")

    # Преобразуем пользователя в Pydantic-модель
    user_data = await serialize_orm_object(user, UserRead)

    return {"user": user_data, "collective": collective_data}