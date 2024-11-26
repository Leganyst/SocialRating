from pydantic import BaseModel, Field
from typing import Optional

from app.models.user import UserRoles


class UserBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    vk_id: str = Field(..., description="VK ID пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя")
    rice: int = Field(..., description="Количество собранного риса")
    role: UserRoles = Field(..., description="Роль пользователя")
    clicks: int = Field(..., description="Количество кликов пользователя")
    invited_users: int = Field(..., description="Количество приглашенных пользователей")
    achievements_count: int = Field(..., description="Количество достижений пользователя")
    social_rating: int = Field(..., description="Социальный рейтинг пользователя")
    current_core: Optional[str] = Field(None, description="Название текущего стержня пользователя")
    collective_id: Optional[int] = Field(None, description="ID коллектива, к которому принадлежит пользователь")

    class Config:
        from_attributes = True


class UserRead(UserBase):
    pass


class UserCreate(BaseModel):
    vk_id: str = Field(..., description="VK ID нового пользователя")
    username: Optional[str] = Field(None, description="Имя нового пользователя")
    role: UserRoles = Field(..., description="Роль нового пользователя")
    rice: int = Field(..., description="Количество собранного риса нового пользователя")
    clicks: int = Field(..., description="Количество кликов нового пользователя")
    invited_users: int = Field(..., description="Количество приглашенных пользователей нового пользователя")
    achievements_count: int = Field(..., description="Количество достижений нового пользователя")
    social_rating: int = Field(..., description="Социальный рейтинг нового пользователя")
    current_core: Optional[str] = Field(None, description="Название текущего стержня нового пользователя")
    collective_id: Optional[int] = Field(None, description="ID коллектива, к которому принадлежит новый пользователь")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="Обновленное имя пользователя")
    social_rating: Optional[int] = Field(None, description="Обновленный социальный рейтинг пользователя")
    rice: Optional[int] = Field(None, description="Обновленное количество собранного риса")
    clicks: Optional[int] = Field(None, description="Обновленное количество кликов пользователя")
    collective_id: Optional[int] = Field(None, description="Обновленный ID коллектива пользователя")
