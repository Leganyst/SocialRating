from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.core.database import Base
from app.models.user import User

class Collective(Base):
    __tablename__ = 'collectives'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    social_rating: Mapped[int] = mapped_column(Integer, default=0)
    members: Mapped[list['User']] = relationship('User', back_populates='collective')
