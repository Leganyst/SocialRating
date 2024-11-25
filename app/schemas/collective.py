from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.collective import CollectiveType  # Импортируем Enum из модели

class CollectiveBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор коллектива")
    name: str = Field(..., description="Название коллектива")
    social_rating: int = Field(..., description="Общий социальный рейтинг коллектива")
    type: CollectiveType = Field(..., description="Тип коллектива (например, 'Начальный совхоз')")
    bonus: Optional[str] = Field(None, description="Бонусы текущего уровня коллектива")
    group_id: str = Field(..., description="Уникальный идентификатор группы VK, связанной с коллективом")


    class Config:
        from_attributes = True

class CollectiveCreate(BaseModel):
    name: str = Field(..., description="Название нового коллектива")
    group_id: str = Field(..., description="Уникальный идентификатор группы VK, связанной с коллективом")
    type: CollectiveType = Field(default=CollectiveType.INITIAL, description="Тип нового коллектива (по умолчанию 'Начальный совхоз')")



class CollectiveRead(CollectiveBase):
    """
    Схема для чтения данных коллектива.
    """
    pass

class CollectiveUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновленное название коллектива")
    bonus: Optional[str] = Field(None, description="Обновленные бонусы коллектива")
    group_id: Optional[str] = Field(None, description="Обновленный идентификатор группы VK, связанной с коллективом")
    type: Optional[CollectiveType] = Field(None, description="Обновленный тип коллектива")

