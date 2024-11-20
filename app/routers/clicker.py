from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.schemas.user import UserRead
from app.crud.user import update_collective_rating, update_user_rice, update_user_rice_and_rating
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.collective import Collective


router = APIRouter(
    prefix="/clicker",
    tags=["Clicker"],
)

@router.post(
    "/",
    summary="Обновление риса пользователя через кликер",
    description="""
        Ручка кликера, позволяющая пользователю добавлять заработанный рис.
        - Если количество риса превышает 100 за один запрос, возвращается ошибка "Жульничество".
        - Итоговое количество риса перерасчитывается с учетом активных бонусов.
        - Обновляет количество риса у пользователя и сохраняет изменения в базе.
    """,
    response_model=dict,
    responses={
        200: {
            "description": "Рис успешно обновлен.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "added_rice": 120,
                        "total_rice": 500
                    }
                }
            },
        },
        400: {"description": "Количество риса превышает допустимый лимит (жульничество)."},
        401: {"description": "Пользователь не авторизован."},
    },
)
async def clicker_update(
    earned_rice: int,
    user: UserRead = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Ручка кликера для обновления количества риса пользователя.
    """
    # Проверка лимита риса
    if earned_rice > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Жульничество: превышено количество риса за один запрос."
        )

    # Перерасчет риса с учетом активных бонусов
    rice_multiplier = 1
    for bonus in user.active_bonuses:
        if bonus.bonus_type == "active":
            rice_multiplier += bonus.effect / 100

    # Итоговое количество риса с учетом бонусов
    total_rice_to_add = int(earned_rice * rice_multiplier)

    # Обновление риса в базе данных
    updated_user = await update_user_rice(session, user.id, total_rice_to_add)

    return {
        "status": "success",
        "added_rice": total_rice_to_add,
        "total_rice": updated_user.rice
    }


@router.post(
    "/convert_rice_to_rating",
    summary="Перерасчет риса в рейтинг",
    description="""
        Переводит указанное количество риса в социальный рейтинг:
        - 100 риса = 1 рейтинг.
        - Списывает указанное количество риса из профиля пользователя.
        - Добавляет рейтинг в профиль пользователя и его совхоза (если пользователь состоит в совхозе).
    """,
    response_model=dict,
    responses={
        200: {
            "description": "Рис успешно преобразован в рейтинг.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "converted_rice": 500,
                        "added_rating": 5,
                        "user_total_rating": 20,
                        "collective_total_rating": 200
                    }
                }
            },
        },
        400: {"description": "Недостаточно риса или минимальное количество для перевода не достигнуто."},
        401: {"description": "Пользователь не авторизован."},
    },
)
async def convert_rice_to_rating(
    rice_to_convert: int,
    user: UserRead = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Ручка перерасчета риса в рейтинг.
    """
    # Проверяем минимальное количество риса
    if rice_to_convert < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальное количество риса для перерасчета — 100."
        )

    # Проверяем, есть ли у пользователя достаточно риса
    if rice_to_convert > user.rice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно риса для перерасчета."
        )

    # Расчет добавляемого рейтинга
    added_rating = rice_to_convert // 100

    # Обновление риса и рейтинга пользователя
    await update_user_rice_and_rating(session, user.id, rice_to_convert, added_rating)

    # Явная предзагрузка значения social_rating
    result = await session.execute(
        select(User.social_rating).where(User.id == user.id)
    )
    user_total_rating = result.scalar_one()

    # Обновление рейтинга совхоза, если пользователь связан с ним
    collective_total_rating = None
    if user.collective_id:
        collective_result = await session.execute(
            select(Collective.social_rating).where(Collective.id == user.collective_id)
        )
        collective_total_rating = collective_result.scalar_one()

        # Обновление совхоза
        await session.execute(
            select(Collective).where(Collective.id == user.collective_id)
        )
        await update_collective_rating(session, user.collective_id, added_rating)

    # Возвращаем результат с заранее загруженными значениями
    return {
        "status": "success",
        "converted_rice": rice_to_convert,
        "added_rating": added_rating,
        "user_total_rating": user_total_rating,
        "collective_total_rating": collective_total_rating or 0
    }
