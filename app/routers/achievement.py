from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.crud.achievement import get_achievement, can_assign_achievement, get_all_achievements, get_user_achievements
from app.models.user import User
from app.schemas.achievement import AchievementRead, UserAchievementRead
from app.schemas.user import UserRead
from app.core.logger import logger
from app.services.achievement_service import add_user_achievement

router = APIRouter(
    tags=["Achievements"],
)


@router.get("/achievements/user", response_model=list[UserAchievementRead], summary="Получить достижения пользователя")
async def get_user_achievements_endpoint(
    user: UserRead = Depends(get_user_depend),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает список достижений, которыми обладает пользователь.
    """
    try:
        # Получаем достижения пользователя
        achievements = await get_user_achievements(db, user_id=user.id)
        if not achievements:
            return []

        # Преобразуем их в формат Pydantic
        return [
            UserAchievementRead(
                achievement=AchievementRead.model_validate(ach.achievement),
                progress=ach.progress,
                is_completed=ach.is_completed,
                last_updated=ach.last_updated,
            )
            for ach in achievements if ach.achievement is not None
        ]
    except Exception as e:
        logger.error(f"Ошибка при получении достижений пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при обработке запроса.",
        )

@router.get(
    "/achievements/",
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
    "/achievements/assign/{achievement_id}",
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
