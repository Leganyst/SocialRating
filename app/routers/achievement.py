from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.crud.achievement import get_achievement, can_assign_achievement, add_user_achievement, get_all_achievements
from app.models.user import User
from app.schemas.achievement import AchievementRead

router = APIRouter(
    prefix="/achievements",
    tags=["Achievements"],
)


@router.get(
    "/",
    summary="Получить список всех достижений",
    description="Возвращает список всех доступных достижений в системе.",
    response_model=list[AchievementRead],
)
async def get_all_achievements_endpoint(session: AsyncSession = Depends(get_db)):
    """
    Ручка для получения списка всех доступных достижений.
    """
    achievements = await get_all_achievements(session)
    if not achievements:
        raise HTTPException(status_code=404, detail="Достижения не найдены.")
    return achievements


@router.post(
    "/assign/{achievement_id}",
    summary="Начислить достижение пользователю",
    description="""
        Начисляет достижение пользователю.
        Учитывается трекинг времени для ежедневных и еженедельных достижений.
    """,
    response_model=dict,
)
async def assign_achievement(
    achievement_id: int,
    user: User = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Ручка для начисления достижения пользователю.
    """
    achievement = await get_achievement(session, achievement_id)
    if not achievement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Достижение не найдено.")

    if not await can_assign_achievement(session, user.id, achievement):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Достижение '{achievement.name}' нельзя получить повторно в данный момент."
        )

    user_achievement = await add_user_achievement(session, user.id, achievement_id)

    return {
        "status": "success",
        "user_id": user.id,
        "achievement_id": achievement.id,
        "achievement_name": achievement.name,
        "achievement_type": achievement.type.value,
    }




