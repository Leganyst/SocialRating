from app.services.user_service import create_or_update_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def handle_authentication(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Выполняет аутентификацию и обработку пользователя и коллектива.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK.
    :return: Словарь с данными пользователя и коллектива.
    """
    result = await create_or_update_user(session, vk_id, group_id)
    return result
