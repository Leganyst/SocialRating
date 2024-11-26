import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Путь для хранения логов
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Создание обработчика для записи логов в файл
file_handler = RotatingFileHandler(
    LOG_DIR / "app.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Для вывода в консоль
        file_handler,  # Для записи в файл
    ],
)

logger = logging.getLogger("SocialRating")
