from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.achievement import AchievementType  # Импортируем Enum из модели

class AchievementBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор достижения", example=1)
    name: str = Field(..., description="Название достижения", example="Первое достижение")
    description: str = Field(..., description="Описание достижения", example="Получено за первое действие")
    condition: str = Field(..., description="Условие получения достижения", example="Сделать что-то впервые")
    bonus: str = Field(..., description="Бонус за получение достижения", example="100 очков")
    visual: Optional[str] = Field(None, description="Путь к изображению достижения", example="/images/achievement1.png")
    type: AchievementType = Field(..., description="Тип достижения", example="UNIQUE")

    class Config:
        from_attributes = True


class AchievementCreate(BaseModel):
    name: str = Field(..., description="Название нового достижения", example="Новое достижение")
    description: str = Field(..., description="Описание нового достижения", example="Получено за новое действие")
    condition: str = Field(..., description="Условие для получения нового достижения", example="Сделать что-то новое")
    bonus: str = Field(..., description="Бонус за получение нового достижения", example="200 очков")
    visual: Optional[str] = Field(None, description="Путь к изображению нового достижения", example="/images/achievement2.png")
    type: AchievementType = Field(..., description="Тип нового достижения", example="UNIQUE")

    class Config:
        from_attributes = True

class AchievementRead(AchievementBase):
    pass


class AchievementUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновлённое название достижения", example="Обновлённое достижение")
    description: Optional[str] = Field(None, description="Обновлённое описание достижения", example="Обновлённое описание")
    condition: Optional[str] = Field(None, description="Обновлённое условие получения достижения", example="Обновлённое условие")
    bonus: Optional[str] = Field(None, description="Обновлённый бонус достижения", example="300 очков")
    visual: Optional[str] = Field(None, description="Обновлённый путь к изображению достижения", example="/images/achievement3.png")


class UserAchievementRead(BaseModel):
    """
    Модель данных о достижении пользователя с текущим прогрессом, статусом и метаданными.
    """
    achievement: AchievementRead = Field(
        ...,
        title="Данные достижения",
        description="Полная информация о достижении, включая название, описание, бонус и другие данные."
    )
    progress: int = Field(
        ...,
        title="Текущий прогресс",
        description="Количество выполненных шагов или накопленных значений для достижения цели.",
        example=75
    )
    is_completed: bool = Field(
        ...,
        title="Статус выполнения",
        description="Флаг, указывающий, завершено ли достижение.",
        example=True
    )
    last_updated: datetime = Field(
        ...,
        title="Последнее обновление",
        description="Дата и время последнего обновления прогресса достижения.",
        example="2024-12-01T12:00:00+00:00"
    )

    class Config:
        from_attributes = True