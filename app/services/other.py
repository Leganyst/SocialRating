from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Type, Any
from pydantic import BaseModel

async def serialize_orm_object(obj: Any, schema: Type[BaseModel]) -> Dict:
    """
    Универсальная функция для преобразования ORM-объекта в Pydantic-модель.

    :param obj: ORM-объект для преобразования.
    :param schema: Pydantic-модель для сериализации.
    :return: Данные, сериализованные в словарь.
    """
    if obj is None:
        return {}

    return schema.from_orm(obj).dict()