from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import CoreType
from app.routers.dependencies.auth import get_user_depend
from app.crud.user import update_user_rice, update_user_rice_and_rating
from app.crud.collective import get_collective, update_collective_rating
from app.models.collective import Collective
from app.schemas.user import UserBase
from app.core.logger import logger
from sqlalchemy import select

from app.services.collective_service import update_collective_type
from app.services.core_service import determine_new_core_type, update_user_core


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
                        "total_rice": 500,
                        "new_core": "IRON"
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
    personal_bonus = user.rice_bonus / 100
    collective_bonus = user.collective_rice_boost / 100
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

    # Проверяем смену стержня
    current_core = CoreType[updated_user.current_core]
    new_core_type = determine_new_core_type(updated_user.social_rating, current_core)
    new_core = None
    if new_core_type != current_core:
        success = await update_user_core(session, updated_user, new_core_type)
        if success:
            new_core = new_core_type.value
            logger.info(
                f"Смена стержня для пользователя {user.vk_id}:\n"
                f"- Старый стержень: {current_core.value}\n"
                f"- Новый стержень: {new_core}."
            )

    return {
        "status": "success",
        "added_rice": total_rice_added,
        "total_rice": updated_user.rice,
        "new_core": new_core,
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
                        "collective_total_rating": 200,
                        "new_collective_type": "GOLD"
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
    logger.info(f"Пользователь {user.vk_id} начал конвертацию риса в рейтинг. Заявленное количество: {rice_to_convert}.")

    # Проверяем минимальное количество риса для перевода
    if rice_to_convert < 100:
        logger.warning(f"Минимальное количество риса для конвертации не достигнуто: {rice_to_convert}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальное количество риса для перерасчета — 100."
        )

    # Проверяем, достаточно ли риса у пользователя
    if rice_to_convert > user.rice:
        logger.warning(f"Недостаточно риса для конвертации у пользователя {user.vk_id}. Имеется: {user.rice}, требуется: {rice_to_convert}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно риса для перевода."
        )

    # Вычисляем добавляемый рейтинг
    added_rating = rice_to_convert // 100
    logger.info(f"Рассчитанный рейтинг для конвертации: {added_rating}.")

    # Обновляем данные пользователя
    updated_user = await update_user_rice_and_rating(session, user.id, rice_to_convert, added_rating)

    # Обновляем рейтинг совхоза
    collective_total_rating = None
    new_collective_type = None
    if updated_user.collective_id:
        collective = await session.get(Collective, updated_user.collective_id)
        if not collective:
            logger.error(f"Совхоз с ID {updated_user.collective_id} не найден.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Совхоз с ID {updated_user.collective_id} не найден."
            )

        previous_type = collective.type  # Исправлено: заменяем `current_collective_type` на `type`
        previous_rating = collective.social_rating

        # Обновляем рейтинг и тип коллектива
        await update_collective_rating(session, collective.id, added_rating)
        await update_collective_type(session, collective)

        new_collective_type = collective.type  # Исправлено: заменяем `current_collective_type` на `type`
        logger.info(
            f"Обновлён совхоз для пользователя {user.vk_id}:\n"
            f"- Старый тип: {previous_type.localized_name()}\n"
            f"- Новый тип: {new_collective_type.localized_name()}\n"
            f"- Рейтинг до: {previous_rating}\n"
            f"- Рейтинг после: {collective.social_rating}."
        )

        collective_total_rating = collective.social_rating

    return {
        "status": "success",
        "converted_rice": rice_to_convert,
        "added_rating": added_rating,
        "user_total_rating": updated_user.social_rating,
        "collective_total_rating": collective_total_rating or 0,
        "new_collective_type": new_collective_type.localized_name() if new_collective_type else None,
    }
