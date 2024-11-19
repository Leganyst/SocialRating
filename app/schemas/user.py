from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    rice: int = Field(0, description="Количество риса, заработанного пользователем")
    clicks: int = Field(0, description="Количество кликов пользователя")
    invited_users: int = Field(0, description="Количество приглашенных пользователей")
    achievements_count: int = Field(0, description="Количество достижений пользователя")
    social_rating: int = Field(0, description="Социальный рейтинг пользователя")
    collective_id: Optional[int] = Field(None, description="ID совхоза, к которому привязан пользователь")

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    active_bonuses: list = Field(default_factory=list, description="Активные бонусы пользователя")
