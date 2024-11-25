from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collective import Collective
from app.models.user import User
from app.crud.collective import get_collective, create_collective
from app.schemas.collective import CollectiveCreate
from app.utils.vk_api import get_group_info
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.collective import Collective
from app.schemas.collective import CollectiveCreate
from app.utils.vk_api import get_group_info
from app.crud.collective import get_collective, create_collective

async def get_or_create_collective(session: AsyncSession, group_id: str) -> Collective:
    """
    Проверяет существование коллектива или создает новый.

    :param session: Асинхронная сессия SQLAlchemy.
    :param group_id: ID группы VK.
    :return: Объект коллектива.
    """
    # Проверяем наличие коллектива с указанным group_id
    result = await session.execute(
        select(Collective).where(Collective.group_id == group_id)
    )
    collective = result.scalar_one_or_none()

    # Если коллектив не найден, создаем новый
    if not collective:
        group_info = await get_group_info(group_id)  # Функция для получения информации о группе VK
        collective_data = CollectiveCreate(
            name=group_info.get("name", f"Группа {group_id}"),
            social_rating=0,
            group_id=group_id
        )
        collective = await create_collective(session, collective_data)

    return collective