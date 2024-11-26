from app.services.core_service import update_user_core
from app.services.user_service import create_or_update_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def handle_authentication(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Выполняет аутентификацию, обработку пользователя и коллектива, а также проверяет стержень пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK.
    :return: Словарь с данными пользователя и коллектива.
    """
    # Создаем или обновляем пользователя и коллектив
    result = await create_or_update_user(session, vk_id, group_id)

    # Получаем обновленного пользователя
    user = result["user"]

    # Проверяем и обновляем стержень пользователя, если необходимо
    await update_user_core(session, user)

    return result