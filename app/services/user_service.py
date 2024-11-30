from app.models.collective import Collective
from app.models.user import CoreType, User, UserRoles
from app.schemas.user import UserBase, UserCreate, UserRead, UserUpdate
from app.schemas.collective import CollectiveBase, CollectiveCreate
from app.crud.user import create_user, get_user_by_vk_id, update_user, update_user_collective
from app.services.collective_service import get_or_create_collective
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Union
from app.core.logger import logger
from datetime import datetime, timezone

from app.services.other import serialize_orm_object


async def create_or_update_user(
    session: AsyncSession, vk_id: str, group_id: Optional[int] = None
) -> dict:
    """
    Создаёт нового пользователя или обновляет существующего. Обрабатывает привязку к коллективу.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK (если передан).
    :return: Словарь с объектами пользователя и коллектива (если применимо).
    """
    # Получаем пользователя по VK ID
    result = await session.execute(select(User).where(User.vk_id == vk_id))
    user = result.scalar_one_or_none()

    if not user:
        # Создаём нового пользователя
        user = User(
            vk_id=vk_id,
            is_invited=False,
            role=UserRoles.user,
            rice=0,
            social_rating=0,
            clicks=0,
            invited_users=0,
            achievements_count=0,
            last_entry=datetime.now(timezone.utc),
            current_core=CoreType.COPPER,
            autocollect_rice_bonus=0,
            autocollect_duration_bonus=0,
            rice_bonus=0,
            invited_users_bonus=0,
            current_collective_type=None,
            collective_rice_boost=0,
            collective_autocollect_bonus=0,
            collective_id=None,
            start_collective_id=None,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Привязка к коллективу, если передан group_id
    collective = await session.execute(select(Collective).where(Collective.id == user.collective_id))
    collective = collective.scalar_one_or_none()
    if group_id:
        if not user.collective_id or str(group_id) != str(collective.group_id):
            # Вычитаем рейтинг из старого коллектива (если был)
            if user.collective_id:
                old_collective = await session.get(Collective, user.collective_id)
                if old_collective:
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

    # Получаем данные текущего коллектива, если он уже есть
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
    :param user: Объект пользователя (ORM).
    :param collective: Объект коллектива (ORM).
    """
    if not isinstance(collective, Collective):
        raise TypeError("Передан объект, не являющийся ORM-классом Collective")

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


async def calculate_afk_rice(user: User, last_entry: datetime, current_time: datetime) -> int:
    """
    Рассчитывает количество риса, заработанного в афк-режиме с учетом максимальной длительности автосбора.

    :param user: Объект пользователя.
    :param last_entry: Время последнего захода пользователя.
    :param current_time: Текущее время.
    :return: Количество заработанного риса.
    """
    # Приведение времени к timezone-aware
    if last_entry.tzinfo is None:
        last_entry = last_entry.replace(tzinfo=timezone.utc)

    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    # Рассчитываем прошедшее время в секундах
    elapsed_seconds = (current_time - last_entry).total_seconds()

    # Максимальное время в секундах, на которое распространяется автосбор
    max_afk_seconds = user.autocollect_duration_bonus * 60

    # Ограничиваем время сбора риса максимумом
    effective_seconds = min(elapsed_seconds, max_afk_seconds)

    # Рис, собираемый в секунду
    rice_per_second = user.autocollect_rice_bonus / 3600

    # Вычисляем афк-рис
    afk_rice = int(effective_seconds * rice_per_second)
    
    # Логируем данные для анализа
    logger.info(
        f"\n----- АФК РИС РАСЧЁТ -----\n"
        f"Пользователь ID: {user.id}, VK ID: {user.vk_id}\n"
        f"Прошло времени с последнего входа: {elapsed_seconds:.2f} сек "
        f"({elapsed_seconds / 60:.2f} мин / {elapsed_seconds / 3600:.2f} час).\n"
        f"Максимальное время фарма: {max_afk_seconds:.2f} сек "
        f"({max_afk_seconds / 60:.2f} мин / {max_afk_seconds / 3600:.2f} час).\n"
        f"Учтено времени для расчёта: {effective_seconds:.2f} сек "
        f"({effective_seconds / 60:.2f} мин / {effective_seconds / 3600:.2f} час).\n"
        f"Автосбор в рис/час: {user.autocollect_rice_bonus}, "
        f"что составляет {rice_per_second:.5f} рис/сек.\n"
        f"Заработано афк-рисов: {afk_rice}.\n"
        f"----- КОНЕЦ РАСЧЁТА -----"
    )

    return max(0, afk_rice)
