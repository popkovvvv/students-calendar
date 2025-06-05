# locales/ru.py

TEXTS = {
    # Главное меню
    "welcome": "👋 Привет! Я бот, который поможет тебе просматривать расписание занятий.",
    "button_calendar": "📅 Календарь",
    "button_help": "❓ Помощь",
    "button_language": "🌐 Язык",
    "main_menu": "Главное меню:",
    "button_admin_menu": "👑 Администрирование",

    # Приветствие для студента на старте
    "welcome_student_start": "Привет, студент! 👋 Вот расписание на ближайшую неделю:",

    # Приветствие для администратора на старте
    "welcome_admin_start": "Привет, староста группы! 👋",

    # Помощь
    "help_student": "Привет! Я бот для просмотра расписания.\n\nДоступные команды:\n• /help - показать это сообщение\n• /calendar - открыть меню управления календарем\n\nВы можете использовать кнопку \"События на неделю\" в меню календаря для просмотра расписания.",
    "help_admin": "Привет, администратор!\n\nДоступные команды:\n• /help - показать это сообщение\n• /calendar - открыть меню управления календарем\n• /stats - просмотр статистики бота\n• /broadcast - рассылка сообщений\n\n",

    # Календарь
    "calendar_menu": "Меню календаря:",
    "button_create_event": "Создать событие",
    "button_week_events": "📈 Событий за неделю",
    "button_delete_event": "Удалить событие",
    "button_back": "⬅️ Назад",
    "create_event_name_prompt": "Введите название события:",
    "create_event_date_prompt": "Введите дату события в формате ДД.ММ.ГГГГ:",
    "create_event_date_empty": "Пожалуйста, введите дату события.",
    "create_event_date_invalid": "Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.",
    "create_event_time_prompt": "Введите время начала события в формате ЧЧ:ММ:",
    "create_event_time_empty": "Пожалуйста, введите время начала события.",
    "create_event_time_invalid": "Неверный формат времени. Пожалуйста, используйте формат ЧЧ:ММ.",
    "create_event_duration_prompt": "Введите продолжительность события в часах (например, 1.5 для 1 часа 30 минут):",
    "create_event_duration_invalid": "Неверный формат продолжительности. Пожалуйста, введите число.",
    "create_event_description_prompt": "Введите описание события (или '-' если описания нет):",
    "create_event_success": "Событие успешно создано!\n\nНазвание: {summary}\nНачало: {start_time}\nОкончание: {end_time}\nОписание: {description}",
    "create_event_failed": "Не удалось создать событие. Попробуйте еще раз.",
    "week_events_empty": "На ближайшие 7 дней нет событий.",
    "week_events_header": "События на ближайшие 7 дней:\n\n",
    "week_events_item": "*{summary}*\nВремя: {formatted_time}\nОписание: {description}\nID: `{event_id}`\n\n",
    "no_description": "Нет описания",
    "delete_event_prompt": "Введите ID события, которое хотите удалить:",
    "delete_event_empty_id": "Пожалуйста, введите ID события для удаления.",
    "delete_event_success": "Событие с ID `{event_id}` успешно удалено.",
    "delete_event_failed": "Не удалось удалить событие с ID `{event_id}`. Убедитесь, что ID верен и событие существует.",

    # Язык
    "choose_language": "Выберите язык интерфейса:",
    "language_changed": "Язык успешно изменен на {language_name}.",
    "unknown_language": "Неизвестный язык. Пожалуйста, выберите один из предложенных вариантов.",

    # Администраторские функции (Меню Администрирования)
    "admin_menu": "Меню администрирования:",
    "button_stats": "📈 Статистика",
    "button_broadcast": "📢 Рассылка",
    "button_ban": "🚫 Бан",
    "button_back_to_main": "⬅️ В главное меню",
    "stats_empty": "Статистика пока пуста.",
    "stats_header": "Статистика использования команд:\n\n",
    "stats_item": "`{handler_name}`: `{count}`\n",
    "broadcast_prompt": "Введите сообщение для рассылки всем пользователям:\n\n",
    "broadcast_empty": "Сообщение для рассылки не может быть пустым.",
    "broadcast_sending": "Отправляю сообщение:\n\n{broadcast_text}\n\nВсего пользователей для рассылки: {user_count}...",
    "broadcast_complete": "Рассылка завершена!\nОтправлено: {sent_count}\nНе удалось отправить: {failed_count}",
    "broadcast_cancelled": "Рассылка отменена.",

    # Статистика команд
    "command_start_stats": "Команда /start",
    "command_stats": "Команда /stats",
    "command_broadcast": "Команда /broadcast",
    "command_help": "Команда /help",
    "command_start": "Команда /start (старый ключ)",

    # Ошибка при попытке отправить текст кнопки в рассылке
    "broadcast_button_text_error": "Пожалуйста, введите текст сообщения для рассылки или вернитесь в главное меню.",

    # Общие ошибки/сообщения
    "create_event_api_error": "Не удалось создать событие в Google Calendar. Пожалуйста, проверьте настройки API или попробуйте позже.",
    "error_user_id_not_found": "Не удалось определить ваш User ID. Пожалуйста, попробуйте позже или обратитесь к администратору.",
    "feature_for_students_only": "Эта функция доступна только для студентов.",
} 