from pydantic import BaseModel
from typing import List

class CollectiveBase(BaseModel):
    name: str
    social_rating: int

class CollectiveCreate(CollectiveBase):
    pass

class CollectiveRead(CollectiveBase):
    id: int
    members: List['UserRead']

    class Config:
        orm_mode = True
