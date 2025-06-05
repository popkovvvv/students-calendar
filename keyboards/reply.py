from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config.settings import ADMIN_IDS, LANGUAGES
from typing import Optional
from utils.i18n import get_text # Импортируем функцию локализации
import logging # Импортируем logging
from sqlalchemy.orm import Session # Импортируем Session
from database.database import get_db # Импортируем get_db

logger = logging.getLogger(__name__) # Создаем логгер для этого модуля

def get_main_keyboard(user_id: Optional[int], db: Session = next(get_db())) -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру с кнопками."""
    is_admin = user_id is not None and user_id in ADMIN_IDS
    logger.info(f"get_main_keyboard called for user_id: {user_id}, is_admin: {is_admin}") # Логирование

    # Используем get_text для текстов кнопок, передаем db
    buttons = [
        [KeyboardButton(text=get_text("button_calendar", user_id, db=db))],
        [KeyboardButton(text=get_text("button_help", user_id, db=db))]
    ]

    # Добавляем кнопку "Язык" для всех пользователей, передаем db
    buttons.append([KeyboardButton(text=get_text("button_language", user_id, db=db))])

    # Добавляем кнопку "Администрирование" для администраторов, передаем db
    if is_admin:
        buttons.append([KeyboardButton(text=get_text("button_admin_menu", user_id, db=db))])

    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_calendar_reply_keyboard(user_id: Optional[int], db: Session = next(get_db())) -> ReplyKeyboardMarkup:
    """Создает Reply-клавиатуру с кнопками действий календаря."""
    logger.info(f"get_calendar_reply_keyboard called for user_id: {user_id}")

    if user_id is None:
        logger.warning("get_calendar_reply_keyboard called with user_id is None.")
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)

    is_admin = user_id in ADMIN_IDS
    logger.info(f"User_id {user_id} in ADMIN_IDS: {is_admin}")

    buttons = []
    if is_admin:
        # Кнопки для администратора (только календарные действия), передаем db
        buttons.extend([
            [KeyboardButton(text=get_text("button_create_event", user_id, db=db))],
            [KeyboardButton(text=get_text("button_week_events", user_id, db=db))],
            [KeyboardButton(text=get_text("button_delete_event", user_id, db=db))],
        ])
    else:
        # Кнопки для студента (только просмотр), передаем db
        buttons.append([KeyboardButton(text=get_text("button_week_events", user_id, db=db))])

    # Кнопка "Назад" всегда присутствует, передаем db
    buttons.append([KeyboardButton(text=get_text("button_back", user_id, db=db))])

    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_admin_keyboard(user_id: Optional[int], db: Session = next(get_db())) -> ReplyKeyboardMarkup:
    """Создает Reply-клавиатуру с кнопками административных действий."""
    logger.info(f"get_admin_keyboard called for user_id: {user_id}")

    if user_id is None:
        logger.warning("get_admin_keyboard called with user_id is None.")
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)

    # Кнопки для администратора (статистика, рассылка, бан), передаем db
    buttons = [
        [KeyboardButton(text=get_text("button_stats", user_id, db=db))], # Кнопка "Статистика"
        [KeyboardButton(text=get_text("button_broadcast", user_id, db=db))], # Кнопка "Рассылка"
    ]

    # Кнопка "Назад в главное меню", передаем db
    buttons.append([KeyboardButton(text=get_text("button_back_to_main", user_id, db=db))])

    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_language_selection_keyboard() -> ReplyKeyboardMarkup:
    """Создает Reply-клавиатуру с кнопками для выбора языка."""
    buttons = []
    # Тексты кнопок выбора языка - сами названия языков, которые не локализуем через get_text
    for lang_code, lang_name in LANGUAGES.items():
        buttons.append([KeyboardButton(text=lang_name)])

    # Можно добавить кнопку "Отмена" или "Назад" если нужно, но пока обойдемся без нее.

    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    return keyboard 