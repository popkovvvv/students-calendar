from sqlalchemy.orm import Session
from database.models import User, ButtonStatistic
from sqlalchemy import update, func
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        """Получает пользователя по его ID."""
        logger.debug(f"Fetching user with id: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_id: int, language_code: str) -> User:
        """Создает нового пользователя в базе данных."""
        logger.info(f"Creating new user with id: {user_id}, language: {language_code}")
        db_user = User(id=user_id, language_code=language_code)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user_language(self, user_id: int, language_code: str) -> User | None:
        """Обновляет язык пользователя."""
        logger.info(f"Updating language for user {user_id} to {language_code}")
        self.db.query(User).filter(User.id == user_id).update({"language_code": language_code})
        self.db.commit()
        return self.get_user(user_id)

    def get_all_users(self) -> list[User]:
        """Получает список всех пользователей."""
        logger.debug("Fetching all users for broadcast")
        return self.db.query(User).all()

    # Добавьте другие методы для работы с пользователем по мере необходимости 

# Новый репозиторий для статистики нажатий кнопок
class ButtonStatisticRepository:
    def __init__(self, db: Session):
        self.db = db

    def increment_button_click(self, button_key: str):
        # Используем update для атомарного инкремента счетчика или создания записи, если не существует
        stmt = update(ButtonStatistic).where(ButtonStatistic.button_key == button_key).values(click_count=ButtonStatistic.click_count + 1)
        result = self.db.execute(stmt)

        if result.rowcount == 0:
            # Если запись не была обновлена (не существовала), создаем новую
            stat = ButtonStatistic(button_key=button_key, click_count=1)
            self.db.add(stat)
            logger.debug(f"Created new statistic entry for button '{button_key}' with count 1.")
        else:
             logger.debug(f"Incremented click count for button '{button_key}' using update. Rows affected: {result.rowcount}")

        self.db.commit()

    def get_all_statistics(self):
        logger.debug("Fetching all button statistics.")
        # Возвращаем статистику, отсортированную по убыванию количества кликов
        return self.db.query(ButtonStatistic).order_by(ButtonStatistic.click_count.desc()).all() 