from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, Update
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_message: Dict[int, float] = {}
        
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            current_time = time.time()
            
            if user_id in self.last_message:
                time_passed = current_time - self.last_message[user_id]
                if time_passed < self.rate_limit:
                    if isinstance(event, Message):
                         await event.answer(
                            "⏳ Пожалуйста, подождите немного перед следующим запросом."
                        )
                    return
                    
            self.last_message[user_id] = current_time
        
        return await handler(event, data) 