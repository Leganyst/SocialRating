from datetime import datetime, timezone
from app.crud.collective import update_collective_level
from app.models.user import CoreType
from app.schemas.collective import CollectiveRead
from app.services.collective_service import apply_collective_bonuses, get_or_create_collective, update_collective_type
from app.services.core_service import determine_new_core_type, update_user_core
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
    Аутентификация пользователя, расчёт афк-рисов, обработка привязки к коллективу и обновление стержня.

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

    logger.info(
        f"Пользователь {vk_id} успешно создан/обновлён. Текущие данные пользователя:\n"
        f"- Рис: {user.rice}\n"
        f"- Социальный рейтинг: {user.social_rating}\n"
        f"- Текущий стержень: {user.current_core}\n"
        f"- Коллектив: {collective.id if collective else 'Нет привязки'}."
    )

    # Рассчёт афк-рисов
    current_time = datetime.now(timezone.utc)
    afk_rice = 0
    if user.last_entry:
        afk_rice = await calculate_afk_rice(user, user.last_entry, current_time)
        logger.info(
            f"Рассчитан афк-рис для пользователя {vk_id}:\n"
            f"- Предыдущее время входа: {user.last_entry}\n"
            f"- Текущее время: {current_time}\n"
            f"- Заработано афк-рисов: {afk_rice}\n"
            f"- Рис до начисления: {user.rice}\n"
            f"- Рис после начисления: {user.rice + afk_rice}."
        )
        user.rice += afk_rice

    # Обновление времени последнего входа
    previous_last_entry = user.last_entry
    user.last_entry = current_time
    logger.info(
        f"Обновлено время последнего входа для пользователя {vk_id}:\n"
        f"- Предыдущее значение: {previous_last_entry}\n"
        f"- Новое значение: {user.last_entry}."
    )
    session.add(user)

    # Обработка смены стержня
    current_core = CoreType[user.current_core] if isinstance(user.current_core, str) else user.current_core
    new_core_type = determine_new_core_type(user.social_rating, current_core)
    if new_core_type != current_core:
        previous_core = user.current_core
        success = await update_user_core(session, user, new_core_type)
        if success:
            logger.info(
                f"Пользователь {vk_id} обновил стержень:\n"
                f"- Предыдущий стержень: {previous_core}\n"
                f"- Новый стержень: {new_core_type.value}\n"
                f"- Новый бонус к сбору риса: {user.rice_bonus}%\n"
                f"- Новый бонус за друзей: {user.invited_users_bonus}x."
            )

    # Применение бонусов и обновление уровня коллектива (если коллектив есть)
    collective_data = {}
    if collective:
        previous_collective_rating = collective.social_rating
        await update_collective_type(session, collective)
        await apply_collective_bonuses(session, user, collective)
        collective_data = await serialize_orm_object(collective, CollectiveRead)
        logger.info(
            f"Обновлён коллектив для пользователя {vk_id}:\n"
            f"- ID коллектива: {collective.id}\n"
            f"- Рейтинг коллектива до обновления: {previous_collective_rating}\n"
            f"- Рейтинг коллектива после обновления: {collective.social_rating}."
        )

    # Сериализация данных пользователя
    user_data = await serialize_orm_object(user, UserRead)

    # Сохраняем изменения в базе данных
    await session.commit()
    logger.info(
        f"Аутентификация пользователя {vk_id} завершена. Итоговые данные:\n"
        f"- Рис: {user.rice}\n"
        f"- Социальный рейтинг: {user.social_rating}\n"
        f"- Текущий стержень: {user.current_core}\n"
        f"- Время последнего входа: {user.last_entry}."
    )

    return {"user": user_data, "collective": collective_data}