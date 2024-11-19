from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from app.core.database import Base
# from app.models.bonus import Bonus

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=False, nullable=True)
    rice: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    invited_users: Mapped[int] = mapped_column(Integer, default=0)
    achievements_count: Mapped[int] = mapped_column(Integer, default=0)
    social_rating: Mapped[int] = mapped_column(Integer, default=0)
    collective_id: Mapped[Optional[int]] = mapped_column(ForeignKey('collectives.id'))

    active_bonuses: Mapped[list['Bonus']] = relationship('Bonus', back_populates='user')
    collective: Mapped['Collective'] = relationship('Collective', back_populates='members')

