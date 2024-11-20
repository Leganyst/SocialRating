from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collective import Collective
from app.models.user import User
from app.crud.collective import get_collective, create_collective
from app.schemas.collective import CollectiveCreate
from app.utils.vk_api import get_group_info

async def get_or_create_collective(session: AsyncSession, group_id: int, user: User) -> Collective:
    """
    Получает существующий коллектив или создает новый.

    :param session: Асинхронная сессия SQLAlchemy.
    :param group_id: ID группы VK.
    :param user: Объект пользователя.
    :return: Объект коллектива.
    """
    collective = await get_collective(session, group_id)
    if not collective:
        group_info = await get_group_info(group_id)
        collective = await create_collective(
            session,
            # name=group_info.get("name", f"Группа {group_id}"),
            # social_rating=user.social_rating,
            # first_member=user
            collective_data=CollectiveCreate(
                name=group_info.get("name", f"{group_id}"),
                social_rating=user.social_rating,
                group_id=str(group_id)
            )
        )
    return collective
