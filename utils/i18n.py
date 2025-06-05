# utils/i18n.py

from config.settings import DEFAULT_LANGUAGE, LANGUAGES
import importlib
from typing import Optional, Dict
import logging # Импортируем модуль логирования

# Импортируем зависимости для работы с базой данных и модель User
from sqlalchemy.orm import Session
from database.models import User

logger = logging.getLogger(__name__) # Создаем логгер для этого модуля

# Загружаем локали
loaded_locales = {}
logger.info("Attempting to load locales...") # Лог начала загрузки
for lang_code, lang_name in LANGUAGES.items(): # Перебираем по LANGUAGES, чтобы использовать lang_name в логе
    try:
        module = importlib.import_module(f"locales.{lang_code}")
        loaded_locales[lang_code] = module.TEXTS
        logger.info(f"Successfully loaded locale for language '{lang_name}' ({lang_code}).") # Лог успешной загрузки
    except ModuleNotFoundError:
        logger.warning(f"Locale file for language '{lang_name}' ({lang_code}) not found at 'locales/{lang_code}.py'.") # Лог предупреждения, если файл не найден
    except Exception as e:
        logger.error(f"Error loading locale for language '{lang_name}' ({lang_code}): {e}") # Лог ошибки при загрузке


def get_text(key: str, user_id: Optional[int], db: Optional[Session] = None) -> str:
    """Возвращает локализованный текст по ключу, user_id и сессии базы данных."""
    user_lang = DEFAULT_LANGUAGE # По умолчанию используем язык из настроек

    if user_id is not None and db is not None:
        # Пытаемся получить пользователя из базы данных
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            user_lang = db_user.language_code

    logger.debug(f"Getting text for key '{key}' for user {user_id}. Determined language: {user_lang}") # Лог определяемого языка

    # Если выбранный язык не загружен, используем язык по умолчанию
    if user_lang not in loaded_locales:
         logger.warning(f"Locale for user language '{user_lang}' not loaded. Falling back to default language '{DEFAULT_LANGUAGE}'.") # Лог отката к дефолту
         user_lang = DEFAULT_LANGUAGE

    messages = loaded_locales.get(user_lang, {}) # Получаем сообщения для языка пользователя или пустой словарь

    # Возвращаем текст по ключу. Если ключ не найден, возвращаем ключ как есть или текст по умолчанию на дефолтном языке
    if key not in messages:
        default_messages = loaded_locales.get(DEFAULT_LANGUAGE, {})
        if key in default_messages:
             logger.warning(f"Key '{key}' not found in locale '{user_lang}'. Using text from default locale '{DEFAULT_LANGUAGE}'.") # Лог использования дефолта по ключу
             return default_messages.get(key, key) # Fallback to key if not in default either
        else:
             logger.error(f"Key '{key}' not found in locale '{user_lang}' or default locale '{DEFAULT_LANGUAGE}'. Returning key as is.") # Лог ошибки, если ключ не найден нигде
             return key # Fallback to key

    return messages.get(key, key) # Should not happen if key is in messages, but as a final safety 