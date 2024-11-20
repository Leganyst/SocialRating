from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserRead
from app.models.user import User
from app.models.collective import Collective
from app.services.collective_service import get_or_create_collective
from app.crud.user import update_user_collective

from sqlalchemy.orm import selectinload

from sqlalchemy.orm import selectinload

async def handle_authentication(session: AsyncSession, query_params: dict, group_id: int) -> UserRead:
    """
    Логика аутентификации и привязки пользователя к коллективу.

    :param session: Асинхронная сессия SQLAlchemy.
    :param query_params: Параметры запроса, содержащие данные пользователя.
    :param group_id: ID группы VK.
    :return: Обновленная Pydantic-модель пользователя.
    """
    # Загружаем пользователя вместе с активными бонусами
    result = await session.execute(
        select(User).options(selectinload(User.active_bonuses)).where(User.vk_id == query_params.get("vk_user_id"))
    )
    user_db = result.scalar_one_or_none()

    if user_db:
        # Проверяем привязку к коллективу
        if user_db.collective_id:
            current_collective = await session.get(Collective, user_db.collective_id)
        else:
            current_collective = None

        if not current_collective or current_collective.id != group_id:
            new_collective = await get_or_create_collective(session, group_id, user_db)
            user_db = await update_user_collective(session, user_db, new_collective.id)
    else:
        user_db = User(
            vk_id=query_params.get("vk_user_id"),
            username=None,
            rice=0,
            clicks=0,
            invited_users=0,
            achievements_count=0,
            social_rating=0,
            collective_id=None
        )
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)

        new_collective = await get_or_create_collective(session, group_id, user_db)
        user_db = await update_user_collective(session, user_db, new_collective.id)

    # Гарантируем загрузку active_bonuses
    user_with_bonuses = await session.execute(
        select(User).options(selectinload(User.active_bonuses)).where(User.id == user_db.id)
    )
    user_with_bonuses = user_with_bonuses.scalar_one()

    return UserRead.model_validate(user_with_bonuses)


