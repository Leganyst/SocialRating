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
    image: Optional[str] = Field(None, description="Ссылка на изображение")
    autocollect_rice_bonus: int = Field(0, description="Бонус к автосбору риса (в единицах риса за час)")
    autocollect_duration_bonus: int = Field(0, description="Длительность автосбора (в минутах)")
    rice_bonus: int = Field(0, description="Бонус к ручному сбору риса (%)")
    invited_users_bonus: int = Field(0, description="Бонус к приглашённым пользователям (множитель)")

    class Config:
        from_attributes = True


class BonusCreate(BaseModel):
    name: str = Field(..., description="Название бонуса")
    description: str = Field(..., description="Описание бонуса")
    base_cost: int = Field(..., description="Начальная стоимость бонуса")
    cost_modifier: float = Field(..., description="Модификатор удорожания бонуса")
    max_level: Optional[int] = Field(None, description="Максимальный уровень бонуса")
    effect: str = Field(..., description="Эффект, предоставляемый бонусом")
    image: Optional[str] = Field(None, description="Ссылка на изображение")
    autocollect_rice_bonus: Optional[int] = Field(0, description="Бонус к автосбору риса (в единицах риса за час)")
    autocollect_duration_bonus: Optional[int] = Field(0, description="Длительность автосбора (в минутах)")
    rice_bonus: Optional[int] = Field(0, description="Бонус к ручному сбору риса (%)")
    invited_users_bonus: Optional[int] = Field(0, description="Бонус к приглашённым пользователям (множитель)")


class BonusRead(BonusBase):
    pass


class BonusUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновленное название бонуса")
    description: Optional[str] = Field(None, description="Обновленное описание бонуса")
    base_cost: Optional[int] = Field(None, description="Обновленная начальная стоимость бонуса")
    cost_modifier: Optional[float] = Field(None, description="Обновленный модификатор удорожания бонуса")
    max_level: Optional[int] = Field(None, description="Обновленный максимальный уровень бонуса")
    effect: Optional[str] = Field(None, description="Обновленный эффект бонуса")
    image: Optional[str] = Field(None, description="Обновленная ссылка на изображение")
    autocollect_rice_bonus: Optional[int] = Field(None, description="Обновленный бонус к автосбору риса (в единицах риса за час)")
    autocollect_duration_bonus: Optional[int] = Field(None, description="Обновленная длительность автосбора (в минутах)")
    rice_bonus: Optional[int] = Field(None, description="Обновленный бонус к ручному сбору риса (%)")
    invited_users_bonus: Optional[int] = Field(None, description="Обновленный бонус к приглашённым пользователям (множитель)")


class UserBonusRead(BaseModel):
    user_id: int = Field(..., description="Идентификатор пользователя, связанного с бонусом.")
    bonus_id: int = Field(..., description="Идентификатор бонуса, который был приобретен.")
    level: int = Field(..., description="Текущий уровень бонуса (количество покупок).")
    total_cost: int = Field(..., description="Общая стоимость всех покупок данного бонуса.")


class UserBonusWithLevelRead(BaseModel):
    bonus: BonusRead  # Данные о самом бонусе
    level: int = Field(..., description="Текущий уровень бонуса у пользователя")
