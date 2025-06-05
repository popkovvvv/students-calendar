# filters/admin_filter.py

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union
import logging # Импортируем logging

from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__) # Создаем логгер для этого модуля

class AdminFilter(BaseFilter):
    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        if obj.from_user is None:
            logger.warning("AdminFilter received object with no from_user.") # Логируем случай с отсутствием user
            return False
        user_id = obj.from_user.id
        is_admin = user_id in ADMIN_IDS
        logger.info(f"AdminFilter called for user_id: {user_id}, is_admin: {is_admin}") # Логирование
        return is_admin 