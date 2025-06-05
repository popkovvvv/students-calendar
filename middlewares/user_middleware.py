import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from sqlalchemy.orm import Session
from database.database import get_db
from database.repositories import UserRepository
from config.settings import DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Применяем мидлварь только к сообщениям от пользователей
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None

        if user_id is None:
            logger.error("UserMiddleware: Не удалось определить user_id.")
            # Продолжаем обработку без user_id или можем прекратить, если user_id критичен
            return await handler(event, data)

        # Получаем сессию БД. Используем get_db() как зависимость.
        # Важно: здесь мы получаем новую сессию для каждого события
        db: Session = next(get_db())
        user_repo = UserRepository(db)

        # Ищем пользователя в базе данных
        db_user = user_repo.get_user(user_id)

        if db_user is None:
            # Если пользователь не найден, создаем нового
            logger.info(f"UserMiddleware: New user detected: {user_id}. Creating DB entry.")
            db_user = user_repo.create_user(user_id, DEFAULT_LANGUAGE)

        # Добавляем пользователя из БД и сессию в данные события
        data["db_user"] = db_user
        data["db"] = db # Также передаем сессию, если она нужна в хендлерах напрямую


        try:
            # Передаем управление следующему хендлеру или мидлвари
            return await handler(event, data)
        finally:
            # Закрываем сессию после обработки события
            db.close() 