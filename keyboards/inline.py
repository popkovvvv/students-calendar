from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def get_calendar_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Создать событие",
                    callback_data="create_event"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 События на неделю",
                    callback_data="week_events"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить событие",
                    callback_data="delete_event"
                )
            ]
        ]
    )

def get_event_actions_keyboard(event_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"delete_{event_id}"
                ),
                InlineKeyboardButton(
                    text="✏️ Изменить",
                    callback_data=f"edit_{event_id}"
                )
            ]
        ]
    ) 