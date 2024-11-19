from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class BonusBase(BaseModel):
    name: str = Field(..., description="Название бонуса")
    bonus_type: str = Field(..., description="Тип бонуса (активный, пассивный или для конвертации)")
    effect: int = Field(..., description="Эффект бонуса (например, увеличение дохода)")
    duration: Optional[int] = Field(None, description="Длительность действия бонуса (в секундах)")
    cost: Optional[int] = Field(None, description="Стоимость бонуса")

    model_config = ConfigDict(from_attributes=True)

class BonusCreate(BonusBase):
    pass

class BonusRead(BonusBase):
    id: int = Field(..., description="Уникальный идентификатор бонуса")
