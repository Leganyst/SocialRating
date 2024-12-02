import requests
import json

# Загрузка файла с данными
with open("load_data/bonuses.json", "r", encoding="utf-8") as file:
    bonuses = json.load(file)

url = "http://127.0.0.1:8000/bonuses/"  # Замените на ваш реальный URL
# url = "https://rating.radmate.ru/bonuses/"  # Замените на ваш реальный URL


for bonus in bonuses:
    response = requests.post(url, json=bonus)
    if response.status_code == 200:
        print(f"Бонус '{bonus['name']}' успешно добавлен.")
    else:
        print(f"Ошибка при добавлении бонуса '{bonus['name']}': {response.status_code} {response.text}")
