from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_user_depend
from app.crud.user import update_user_rice, update_user_rice_and_rating
from app.crud.collective import update_collective_rating
from app.models.collective import Collective
from app.schemas.user import UserBase
from app.core.logger import logger
from sqlalchemy import select


router = APIRouter(
    prefix="/clicker",
    tags=["Clicker"],
)


@router.post(
    "/",
    summary="Обновление риса пользователя через кликер",
    description="""
        Обновляет количество риса пользователя.
        - Если пользователь добавляет более 100 риса за один запрос, возвращается ошибка.
        - Учитываются активные бонусы, увеличивающие количество добавляемого риса.
        - Обновляет данные пользователя в базе.
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
        400: {"description": "Количество риса превышает допустимый лимит."},
        401: {"description": "Пользователь не авторизован."},
    },
)
async def clicker_update(
    earned_rice: int,
    user: UserBase = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Обновляет количество риса у пользователя через кликер с учётом бонусов.
    """
    logger.info(f"Пользователь {user.vk_id} начал процесс добавления риса через кликер. Заявленное количество: {earned_rice}.")

    # Проверяем лимит риса за один запрос
    if earned_rice > 100:
        logger.warning(f"Пользователь {user.vk_id} превысил лимит добавления риса. Запрос: {earned_rice} риса.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество риса превышает допустимый лимит."
        )

    # Учитываем бонусы пользователя
    personal_bonus = user.rice_bonus / 100  # Преобразуем в множитель
    collective_bonus = user.collective_rice_boost / 100  # Преобразуем в множитель
    total_bonus = 1 + personal_bonus + collective_bonus

    logger.info(
        f"Бонусы пользователя {user.vk_id}:\n"
        f"- Личный бонус: {personal_bonus * 100}%\n"
        f"- Бонус от совхоза: {collective_bonus * 100}%\n"
        f"- Итоговый множитель: {total_bonus:.2f}"
    )

    # Рассчитываем итоговое количество добавляемого риса
    total_rice_added = int(earned_rice * total_bonus)
    logger.info(f"Пользователь {user.vk_id} заработал {total_rice_added} риса с учётом бонусов.")

    # Обновляем количество риса
    updated_user = await update_user_rice(session, user.id, total_rice_added)

    logger.info(
        f"Количество риса у пользователя {user.vk_id} успешно обновлено. "
        f"Добавлено риса: {total_rice_added}, всего риса: {updated_user.rice}."
    )

    # Метрики для мониторинга (например, Prometheus)
    # Пример кода для интеграции с метриками
    # metrics.rice_collected_total.labels(user_id=user.vk_id).inc(total_rice_added)

    return {
        "status": "success",
        "added_rice": total_rice_added,
        "total_rice": updated_user.rice
    }



@router.post(
    "/convert_rice_to_rating",
    summary="Конвертация риса в рейтинг",
    description="""
        Переводит рис в социальный рейтинг.
        - 100 риса = 1 рейтинг.
        - Обновляет данные пользователя и его совхоза (если пользователь состоит в коллективе).
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
    user: UserBase = Depends(get_user_depend),
    session: AsyncSession = Depends(get_db),
):
    """
    Конвертация риса в социальный рейтинг.
    """
    # Проверяем минимальное количество риса для перевода
    if rice_to_convert < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальное количество риса для перерасчета — 100."
        )

    # Проверяем, достаточно ли риса у пользователя
    if rice_to_convert > user.rice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно риса для перевода."
        )

    # Вычисляем добавляемый рейтинг
    added_rating = rice_to_convert // 100

    # Обновляем данные пользователя
    updated_user = await update_user_rice_and_rating(session, user.id, rice_to_convert, added_rating)

    # Обновляем рейтинг совхоза, если пользователь состоит в коллективе
    collective_total_rating = None
    if user.collective_id:
        await update_collective_rating(session, user.collective_id, added_rating)
        result = await session.execute(
            select(Collective.social_rating).where(Collective.id == user.collective_id)
        )
        collective_total_rating = result.scalar_one()

    return {
        "status": "success",
        "converted_rice": rice_to_convert,
        "added_rating": added_rating,
        "user_total_rating": updated_user.social_rating,
        "collective_total_rating": collective_total_rating or 0
    }
