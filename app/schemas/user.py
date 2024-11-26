from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.models.user import UserRoles


class UserBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    vk_id: str = Field(..., description="VK ID пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя")
    role: UserRoles = Field(..., description="Роль пользователя")
    
    rice: int = Field(..., description="Количество собранного риса нового пользователя")
    social_rating: int = Field(..., description="Социальный рейтинг нового пользователя")
    clicks: int = Field(..., description="Количество кликов нового пользователя")
    invited_users: int = Field(..., description="Количество приглашенных пользователей нового пользователя")
    achievements_count: int = Field(..., description="Количество достижений нового пользователя")
    last_entry: Optional[datetime] = Field(None, description="Последний вход нового пользователя")
    current_core: Optional[str] = Field(None, description="Название текущего стержня нового пользователя")
      
    autocollect_rice_bonus: int = Field(..., description="Бонус к автосбору риса нового пользователя в единицах риса за час")
    autocollect_duration_bonus: int = Field(..., description="Длительность автосбора нового пользователя в минутах")
    rice_bonus: int = Field(..., description="Бонус к ручному сбору риса нового пользователя в процентах")
    invited_users_bonus: int = Field(..., description="Бонус к приглашенным пользователям нового пользователя в виде множителя")
       
   
    collective_id: Optional[int] = Field(None, description="ID коллектива, к которому принадлежит пользователь")

    class Config:
        from_attributes = True


class UserRead(UserBase):
    pass


class UserCreate(BaseModel):
    vk_id: str = Field(..., description="VK ID нового пользователя")
    username: Optional[str] = Field(None, description="Имя нового пользователя")
    is_invited: bool = Field(..., description="Приглашен ли уже пользователь")
    role: UserRoles = Field(..., description="Роль нового пользователя")
    
    rice: int = Field(..., description="Количество собранного риса нового пользователя")
    social_rating: int = Field(..., description="Социальный рейтинг нового пользователя")
    clicks: int = Field(..., description="Количество кликов нового пользователя")
    invited_users: int = Field(..., description="Количество приглашенных пользователей нового пользователя")
    achievements_count: int = Field(..., description="Количество достижений нового пользователя")
    last_entry: Optional[datetime] = Field(None, description="Последний вход нового пользователя")
    current_core: Optional[str] = Field(None, description="Название текущего стержня нового пользователя")
    

    collective_id: Optional[int] = Field(None, description="ID коллектива, к которому принадлежит новый пользователь")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="Обновленное имя пользователя")
    social_rating: Optional[int] = Field(None, description="Обновленный социальный рейтинг пользователя")
    rice: Optional[int] = Field(None, description="Обновленное количество собранного риса")
    clicks: Optional[int] = Field(None, description="Обновленное количество кликов пользователя")
    collective_id: Optional[int] = Field(None, description="Обновленный ID коллектива пользователя")
