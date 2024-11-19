from pydantic import BaseModel
from typing import Optional

class BonusBase(BaseModel):
    name: str
    bonus_type: str
    effect: int
    duration: Optional[int]
    cost: Optional[int]

class BonusCreate(BonusBase):
    user_id: Optional[int]

class BonusRead(BonusBase):
    id: int

    class Config:
        orm_mode = True
