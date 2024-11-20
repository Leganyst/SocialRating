import httpx
from app.core.config import settings

async def get_group_info(group_id: int) -> dict:
    """
    Получение информации о группе через VK API.

    :param group_id: ID группы VK.
    :return: Словарь с данными группы. 
             Формат ответа включает следующие поля:

    - **id** (int): Идентификатор сообщества.
    - **name** (str): Название сообщества.
    - **screen_name** (str): Короткое имя сообщества.
    - **is_closed** (int): Информация о закрытости сообщества:
        - `0` — открытое.
        - `1` — закрытое.
        - `2` — приватное.
    - **type** (str): Тип сообщества:
        - `group` — группа.
        - `page` — публичная страница.
        - `event` — мероприятие.
    - **photo_50** (str): URL фотографии сообщества размером 50x50.
    - **photo_100** (str): URL фотографии сообщества размером 100x100.
    - **photo_200** (str): URL фотографии сообщества размером 200x200.
    - **activity** (str, optional): Описание активности сообщества (если доступно).
    - **members_count** (int, optional): Количество участников в сообществе (если доступно).
    - **description** (str, optional): Описание сообщества (если доступно).
    - **contacts** (list, optional): Контакты сообщества (если доступны).
    - **links** (list, optional): Ссылки сообщества (если доступны).
    - **status** (str, optional): Статус сообщества (если доступен).
    - **site** (str, optional): Сайт сообщества (если доступен).

    Возможны дополнительные поля в зависимости от настроек сообщества или разрешений API.
    """
    url = f"https://api.vk.com/method/groups.getById"
    params = {
        "group_id": group_id,
        "access_token": settings.application_secret_key,
        "v": "5.131"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if "response" not in data or not data["response"]:
        raise ValueError("Invalid response from VK API")

    return data["response"][0]  # Возвращаем данные первой (и единственной) группы в ответе
