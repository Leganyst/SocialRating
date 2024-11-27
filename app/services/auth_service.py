from app.crud.collective import update_collective_level
from app.schemas.collective import CollectiveRead
from app.services.collective_service import apply_collective_bonuses, update_collective_type
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
    Выполняет аутентификацию пользователя и обработку совхоза.
    """
    logger.info(f"Начата аутентификация пользователя {vk_id}.")
    
    # Создание или обновление пользователя
    result = await create_or_update_user(session, vk_id, group_id)
    user = result["user"]

    collective_data = {}
    if user.collective_id:
        collective = await session.get(Collective, user.collective_id)
        if not collective:
            logger.error(f"Не удалось найти совхоз для пользователя {user.vk_id}.")
            raise ValueError("Совхоз не найден.")

        # Обновление уровня совхоза
        updated = await update_collective_type(session, collective)

        # Применение бонусов пользователю
        await apply_collective_bonuses(session, user, collective)

        # Сериализация коллектива
        collective_data = await serialize_orm_object(collective, CollectiveRead)

    # Сериализация пользователя
    user_data = await serialize_orm_object(user, UserRead)

    return {"user": user_data, "collective": collective_data}
