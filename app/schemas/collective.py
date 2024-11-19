from pydantic import BaseModel, ConfigDict, Field
from typing import List

class CollectiveBase(BaseModel):
    name: str = Field(..., description="Название совхоза")
    social_rating: int = Field(0, description="Социальный рейтинг совхоза")

    model_config = ConfigDict(from_attributes=True)

class CollectiveCreate(CollectiveBase):
    pass

class CollectiveRead(CollectiveBase):
    id: int = Field(..., description="Уникальный идентификатор совхоза")
    members: List = Field(default_factory=list, description="Список участников совхоза")
