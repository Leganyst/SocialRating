from app.models.collective import Collective
from app.models.user import User
from app.schemas.user import UserBase
from app.schemas.collective import CollectiveBase, CollectiveCreate
from app.crud.user import get_user_by_vk_id, update_user_collective
from app.services.collective_service import get_or_create_collective
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.logger import logger
from datetime import datetime, timezone


async def create_or_update_user(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Создает нового пользователя или обновляет его привязку к группе.
    
    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK.
    :return: Словарь с данными пользователя и объекта коллектива (если применимо).
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
            "collective_id": None,
            "start_collective_id": None,  # Стартовый коллектив добавим позже
        }
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Если указан group_id, проверяем или обновляем привязку к коллективу
    collective = None
    if group_id:
        if not user.collective_id or str(group_id) != str(user.collective_id):
            # Вычитаем рейтинг из старого коллектива
            if user.collective_id:
                await subtract_user_rating_from_collective(session, user)

            # Создаем или получаем новый коллектив
            collective = await get_or_create_collective(session, group_id)
            user.collective_id = collective.id

            # Добавляем рейтинг к новому коллективу
            await add_user_rating_to_collective(session, user, collective)

        # Если у пользователя нет стартового коллектива, устанавливаем его
        if not user.start_collective_id:
            user.start_collective_id = user.collective_id

        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Получаем данные текущего коллектива
    if user.collective_id and not collective:
        collective = await session.get(Collective, user.collective_id)

    return {"user": user, "collective": collective}


async def subtract_user_rating_from_collective(session: AsyncSession, user: User):
    """
    Уменьшает социальный рейтинг коллектива, в котором состоит пользователь.
    
    :param session: Асинхронная сессия SQLAlchemy.
    :param user: Объект пользователя.
    """
    if user.collective_id:
        collective = await session.get(Collective, user.collective_id)
        if collective:
            collective.social_rating -= user.social_rating
            session.add(collective)
            await session.commit()
            logger.info(
                f"Уменьшен социальный рейтинг коллектива '{collective.name}' (ID: {collective.id}). "
                f"Новое значение: {collective.social_rating}."
            )


async def add_user_rating_to_collective(session: AsyncSession, user: User, collective: Collective):
    """
    Увеличивает социальный рейтинг указанного коллектива на величину рейтинга пользователя.
    
    :param session: Асинхронная сессия SQLAlchemy.
    :param user: Объект пользователя.
    :param collective: Объект коллектива.
    """
    collective.social_rating += user.social_rating
    session.add(collective)
    await session.commit()
    logger.info(
        f"Увеличен социальный рейтинг коллектива '{collective.name}' (ID: {collective.id}). "
        f"Новое значение: {collective.social_rating}."
    )
    
    
async def get_user_data(session: AsyncSession, user_id: int) -> dict:
    """
    Возвращает данные пользователя, включая время с последнего входа.
    """
    user = await session.get(User, user_id)
    if not user:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    # Рассчитываем время с последнего входа
    time_since_last_entry = datetime.now(timezone.utc) - user.last_entry
    time_in_afk = time_since_last_entry.total_seconds()  # Время в секундах
    afk_hours = time_in_afk / 3600  # Время в часах

    # Формируем ответ с данными пользователя
    user_data = {
        "vk_id": user.vk_id,
        "rice": user.rice,
        "social_rating": user.social_rating,
        "time_since_last_entry": afk_hours,  # Время афк в часах
    }

    return user_data

