from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collective import Collective, collective_factory
from app.models.user import User
from app.crud.collective import get_collective, create_collective
from app.schemas.collective import CollectiveCreate
from app.utils.vk_api import get_group_info
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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


async def apply_collective_bonuses(session: AsyncSession, collective: Collective):
    """
    Применяет бонусы совхоза к его участникам.

    :param session: Асинхронная сессия SQLAlchemy.
    :param collective: Объект текущего коллектива.
    """
    bonuses = collective_factory(collective.type)
    collective_members = await session.execute(
        select(User).options(selectinload(User.collective)).where(User.collective_id == collective.id)
    )
    collective_members = collective_members.scalars().all()
    for user in collective_members:
        # Применяем бонусы
        user.rice_bonus += int(bonuses["rice_boost"] * 100)  # Конвертируем множитель в проценты
        user.autocollect_rice_bonus += int(bonuses["autocollect_bonus"] * 100)
        session.add(user)

    await session.commit()
