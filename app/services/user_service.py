from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.crud.user import get_user_by_vk_id, update_user_collective
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.collective_service import get_or_create_collective

async def create_or_update_user(session: AsyncSession, vk_id: str, group_id: Optional[int] = None) -> dict:
    """
    Создает нового пользователя или обновляет его привязку к группе.

    :param session: Асинхронная сессия SQLAlchemy.
    :param vk_id: VK ID пользователя.
    :param group_id: ID группы VK.
    :return: Словарь с данными пользователя и коллектива (если применимо).
    """
    # Пытаемся получить пользователя по VK ID с предзагрузкой зависимостей
    result = await session.execute(
        select(User)
        .options(selectinload(User.active_bonuses), selectinload(User.collective))
        .where(User.vk_id == vk_id)
    )
    user = result.scalar_one_or_none()

    # Если пользователь не существует, создаем нового
    if not user:
        user_data = UserCreate(
            vk_id=vk_id,
            username=None,
            rice=0,
            clicks=0,
            invited_users=0,
            achievements_count=0,
            social_rating=0,
            collective_id=None
        )
        user = User(**user_data.model_dump())
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Если указан group_id, проверяем или обновляем привязку к группе
    collective = None
    if group_id:
        if not user.collective_id or not user.collective or user.collective.group_id != str(group_id):
            collective = await get_or_create_collective(session, group_id)
            user = await update_user_collective(session, user, collective.id)

    # Заново загружаем пользователя с зависимостями для корректной сериализации
    result = await session.execute(
        select(User)
        .options(selectinload(User.active_bonuses), selectinload(User.collective))
        .where(User.id == user.id)
    )
    user = result.scalar_one()

    return {
        "user": UserRead.model_validate(user),
        "collective": collective
    }