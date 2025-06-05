import logging
import sys
from pathlib import Path

def setup_logger():
    # Создаем директорию для логов, если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка файлового хендлера
    file_handler = logging.FileHandler(
        filename=log_dir / "bot.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Настройка консольного хендлера
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler) 