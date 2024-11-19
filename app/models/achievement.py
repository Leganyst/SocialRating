from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.core.database import Base

class Achievement(Base):
    __tablename__ = 'achievements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    condition: Mapped[str] = mapped_column(String, nullable=False)
    reward: Mapped[str] = mapped_column(String, nullable=False)
