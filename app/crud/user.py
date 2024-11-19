from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

# Create
async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
    user = User(vk_id=user_data.vk_id, phone=user_data.phone)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)

# Read by ID
async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    return UserRead.model_validate(user) if user else None

# Read by VK ID
async def get_user_by_vk_id(db: AsyncSession, vk_id: str) -> UserRead:
    result = await db.execute(select(User).filter(User.vk_id == vk_id))
    user = result.scalars().first()
    return UserRead.model_validate(user) if user else None

# Update
async def update_user(db: AsyncSession, user_id: int, user_data: UserCreate) -> UserRead:
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(vk_id=user_data.vk_id, phone=user_data.phone)
        .returning(User)
    )
    user = result.scalar_one_or_none()
    await db.commit()
    return UserRead.model_validate(user) if user else None

# Delete
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    return result.rowcount > 0
