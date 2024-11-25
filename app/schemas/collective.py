from pydantic import BaseModel, Field
from typing import Optional


class CollectiveBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор коллектива")
    name: str = Field(..., description="Название коллектива")
    social_rating: int = Field(..., description="Общий социальный рейтинг коллектива")
    type: str = Field(..., description="Тип коллектива (например, 'Начальный совхоз')")
    bonus: Optional[str] = Field(None, description="Бонусы текущего уровня коллектива")

    class Config:
        orm_mode = True


class CollectiveCreate(BaseModel):
    name: str = Field(..., description="Название нового коллектива")


class CollectiveRead(CollectiveBase):
    pass


class CollectiveUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновленное название коллектива")
    bonus: Optional[str] = Field(None, description="Обновленные бонусы коллектива")
