from pydantic import BaseModel

class AchievementBase(BaseModel):
    name: str
    condition: str
    reward: str

class AchievementCreate(AchievementBase):
    pass

class AchievementRead(AchievementBase):
    id: int

    class Config:
        orm_mode = True
