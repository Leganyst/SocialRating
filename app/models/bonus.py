from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from app.core.database import Base
# from app.models.user import User
from typing import Optional

class Bonus(Base):
    __tablename__ = 'bonuses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    bonus_type: Mapped[str] = mapped_column(String, nullable=False)
    effect: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    cost: Mapped[Optional[int]] = mapped_column(Integer)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='active_bonuses')
