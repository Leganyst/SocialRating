from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.achievement import AchievementType  # Импортируем Enum из модели


class AchievementBase(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор достижения", example=1)
    name: str = Field(..., description="Название достижения", example="Первое достижение")
    description: str = Field(..., description="Описание достижения", example="Получено за первое действие")
    condition: str = Field(..., description="Условие получения достижения", example="Сделать что-то впервые")
    visual: Optional[str] = Field(None, description="Путь к изображению достижения", example="/images/achievement1.png")
    type: AchievementType = Field(..., description="Тип достижения", example="UNIQUE")
    is_active: bool = Field(..., description="Активно ли достижение", example=True)

    # Новые поля для бонусов
    social_rating_bonus: int = Field(
        0, description="Бонус к социальному рейтингу", example=100
    )
    rice_production_bonus: float = Field(
        0.0, description="Процентный бонус к добыче риса", example=20.0
    )
    autocollect_duration_bonus: float = Field(
        0.0, description="Процентный бонус к времени автосбора", example=15.0
    )

    class Config:
        from_attributes = True


class AchievementCreate(BaseModel):
    name: str = Field(..., description="Название нового достижения", example="Новое достижение")
    description: str = Field(..., description="Описание нового достижения", example="Получено за новое действие")
    condition: str = Field(..., description="Условие для получения нового достижения", example="Сделать что-то новое")
    visual: Optional[str] = Field(None, description="Путь к изображению нового достижения", example="/images/achievement2.png")
    type: AchievementType = Field(..., description="Тип нового достижения", example="UNIQUE")
    is_active: bool = Field(..., description="Активно ли достижение", example=True)

    # Новые поля для бонусов
    social_rating_bonus: int = Field(
        0, description="Бонус к социальному рейтингу", example=100
    )
    rice_production_bonus: float = Field(
        0.0, description="Процентный бонус к добыче риса", example=20.0
    )
    autocollect_duration_bonus: float = Field(
        0.0, description="Процентный бонус к времени автосбора", example=15.0
    )

    class Config:
        from_attributes = True


class AchievementRead(AchievementBase):
    pass


class AchievementUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Обновлённое название достижения", example="Обновлённое достижение")
    description: Optional[str] = Field(None, description="Обновлённое описание достижения", example="Обновлённое описание")
    condition: Optional[str] = Field(None, description="Обновлённое условие получения достижения", example="Обновлённое условие")
    visual: Optional[str] = Field(None, description="Обновлённый путь к изображению достижения", example="/images/achievement3.png")
    is_active: Optional[bool] = Field(None, description="Изменение активности достижения", example=True)

    # Новые поля для бонусов
    social_rating_bonus: Optional[int] = Field(
        None, description="Обновлённый бонус к социальному рейтингу", example=200
    )
    rice_production_bonus: Optional[float] = Field(
        None, description="Обновлённый процентный бонус к добыче риса", example=25.0
    )
    autocollect_duration_bonus: Optional[float] = Field(
        None, description="Обновлённый процентный бонус к времени автосбора", example=10.0
    )


class UserAchievementRead(BaseModel):
    """
    Модель данных о достижении пользователя с текущим прогрессом, статусом и метаданными.
    """
    achievement: AchievementRead = Field(
        ...,
        title="Данные достижения",
        description="Полная информация о достижении, включая название, описание, бонусы и другие данные."
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
