from datetime import datetime, timezone
from app.crud.collective import update_collective_level
from app.schemas.collective import CollectiveRead
from app.services.collective_service import apply_collective_bonuses, get_or_create_collective, update_collective_type
from app.services.other import serialize_orm_object
from app.services.user_service import calculate_afk_rice, create_or_update_user
from app.models.collective import Collective
from app.schemas.user import UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.logger import logger

async def handle_authentication(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Аутентификация пользователя, расчёт афк-рисов и обработка привязки к коллективу.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK (если передан).
    :return: Словарь с данными пользователя и коллектива.
    """
    logger.info(f"Начата аутентификация пользователя {vk_id}.")

    # Создание или обновление пользователя и привязка к коллективу
    user_collective_data = await create_or_update_user(session, vk_id, group_id)
    user = user_collective_data["user"]
    collective = user_collective_data["collective"]

    # Рассчёт афк-рисов
    current_time = datetime.now(timezone.utc)
    if user.last_entry:
        afk_rice = await calculate_afk_rice(user, user.last_entry, current_time)
        logger.info(f"Пользователь {vk_id} заработал {afk_rice} риса в афк режиме.")
        user.rice += afk_rice

    # Обновление времени последнего входа
    user.last_entry = current_time
    session.add(user)

    # Применение бонусов и обновление уровня коллектива (если коллектив есть)
    collective_data = {}
    if collective:
        await apply_collective_bonuses(session, user, collective)
        await update_collective_type(session, collective)
        collective_data = await serialize_orm_object(collective, CollectiveRead)

    # Сериализация данных пользователя
    user_data = await serialize_orm_object(user, UserRead)

    # Сохраняем изменения в базе данных
    await session.commit()

    return {"user": user_data, "collective": collective_data}