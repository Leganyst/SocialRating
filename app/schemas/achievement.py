from pydantic import BaseModel, ConfigDict, Field

class AchievementBase(BaseModel):
    name: str = Field(..., description="Название достижения")
    condition: str = Field(..., description="Условие получения достижения")
    reward: str = Field(..., description="Награда за достижение")

    model_config = ConfigDict(from_attributes=True)

class AchievementCreate(AchievementBase):
    pass

class AchievementRead(AchievementBase):
    id: int = Field(..., description="Уникальный идентификатор достижения")
