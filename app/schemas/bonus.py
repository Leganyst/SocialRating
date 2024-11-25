from pydantic import BaseModel, Field
from typing import Optional


class BonusBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор бонуса")
    name: str = Field(..., description="Название бонуса")
    description: str = Field(..., description="Описание бонуса")
    base_cost: int = Field(..., description="Начальная стоимость бонуса")
    cost_modifier: float = Field(..., description="Модификатор удорожания бонуса")
    max_level: Optional[int] = Field(None, description="Максимальный уровень бонуса")
    effect: str = Field(..., description="Эффект, предоставляемый бонусом")

    class Config:
        orm_mode = True


class BonusCreate(BonusBase):
    pass


class BonusRead(BonusBase):
    pass


class BonusUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновленное название бонуса")
    description: Optional[str] = Field(None, description="Обновленное описание бонуса")
    base_cost: Optional[int] = Field(None, description="Обновленная начальная стоимость бонуса")
    cost_modifier: Optional[float] = Field(None, description="Обновленный модификатор удорожания бонуса")
    max_level: Optional[int] = Field(None, description="Обновленный максимальный уровень бонуса")
    effect: Optional[str] = Field(None, description="Обновленный эффект бонуса")
