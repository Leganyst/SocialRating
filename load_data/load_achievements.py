import requests
import json

# Загрузка файла с данными
with open("./load_data/achievements.json", "r", encoding="utf-8") as file:
    achievements = json.load(file)

url = "http://127.0.0.1:8000/achievements/crud/"  # Замените на ваш реальный URL

for achievement in achievements:
    response = requests.post(url, json=achievement)
    if response.status_code == 200:
        print(f"Достижение '{achievement['name']}' успешно добавлено.")
    else:
        print(f"Ошибка при добавлении достижения '{achievement['name']}': {response.status_code} {response.text}")
