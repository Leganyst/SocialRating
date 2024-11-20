from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from app.models.collective import CollectiveType


class CollectiveBase(BaseModel):
    name: str = Field(..., description="Название совхоза")
    social_rating: int = Field(0, description="Социальный рейтинг совхоза")
    group_id: str = Field(..., description="ID группы совхоза в социальной сети")
    collective_type: Optional[CollectiveType] = Field(CollectiveType.start, description="Тип совхоза")

    model_config = ConfigDict(from_attributes=True)

class CollectiveCreate(CollectiveBase):
    pass

class CollectiveRead(CollectiveBase):
    id: int = Field(..., description="Уникальный идентификатор совхоза")
    members: List = Field(default_factory=list, description="Список участников совхоза")
