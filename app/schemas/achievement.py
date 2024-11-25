from pydantic import BaseModel, Field
from typing import Optional


class AchievementBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор достижения")
    name: str = Field(..., description="Название достижения")
    description: str = Field(..., description="Описание достижения")
    condition: str = Field(..., description="Условие получения достижения")
    bonus: str = Field(..., description="Бонус за получение достижения")
    visual: Optional[str] = Field(None, description="Путь к изображению достижения")

    class Config:
        orm_mode = True


class AchievementCreate(BaseModel):
    name: str = Field(..., description="Название нового достижения")
    description: str = Field(..., description="Описание нового достижения")
    condition: str = Field(..., description="Условие для получения нового достижения")
    bonus: str = Field(..., description="Бонус за получение нового достижения")
    visual: Optional[str] = Field(None, description="Путь к изображению нового достижения")


class AchievementRead(AchievementBase):
    pass


class AchievementUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновлённое название достижения")
    description: Optional[str] = Field(None, description="Обновлённое описание достижения")
    condition: Optional[str] = Field(None, description="Обновлённое условие получения достижения")
    bonus: Optional[str] = Field(None, description="Обновлённый бонус достижения")
    visual: Optional[str] = Field(None, description="Обновлённый путь к изображению достижения")
