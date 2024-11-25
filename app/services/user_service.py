from app.models.user import User
from app.schemas.user import UserBase
from app.schemas.collective import CollectiveBase
from app.crud.user import get_user_by_vk_id, update_user_collective
from app.services.collective_service import get_or_create_collective
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional


async def create_or_update_user(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Создает нового пользователя или обновляет его привязку к группе.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK.
    :return: Словарь с данными пользователя и коллектива (если применимо).
    """
    # Пытаемся получить пользователя по VK ID
    result = await session.execute(select(User).where(User.vk_id == vk_id))
    user = result.scalar_one_or_none()

    # Если пользователь не существует, создаем нового
    if not user:
        user_data = {
            "vk_id": vk_id,
            "username": None,
            "rice": 0,
            "clicks": 0,
            "invited_users": 0,
            "achievements_count": 0,
            "social_rating": 0,
            "collective_id": None
        }
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Если указан group_id, проверяем или обновляем привязку к коллективу
    collective = None
    if group_id and (not user.collective_id or str(group_id) != str(user.collective_id)):
        collective = await get_or_create_collective(session, group_id)
        await update_user_collective(session, vk_id, collective.id)

    # Подготовка данных для возврата
    user_data = UserBase.model_validate(user)  # Используем UserBase для базовой информации о пользователе
    collective_data = CollectiveBase.model_validate(collective) if collective else None

    return {"user": user_data, "collective": collective_data}
