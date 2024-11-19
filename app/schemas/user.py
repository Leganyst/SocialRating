from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    rice: int
    clicks: int
    invited_users: int
    achievements_count: int
    social_rating: int
    collective_id: Optional[int]

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    active_bonuses: List['BonusRead']

    class Config:
        orm_mode = True
