import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, Update
from aiogram.filters import Command, StateFilter
from keyboards.reply import get_main_keyboard, get_calendar_reply_keyboard, get_language_selection_keyboard, get_admin_keyboard
from routers.calendar import cmd_calendar
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
import re # Импортируем модуль re для регулярных выражений
from typing import Optional, Dict, Any, List, TypedDict, Union, cast

# Импортируем зависимости для работы с базой данных
from sqlalchemy.orm import Session
from sqlalchemy import Column
from database.models import User
from database.repositories import UserRepository, ButtonStatisticRepository # Импортируем ButtonStatisticRepository
from database.database import get_db # Импортируем get_db

# Импортируем зависимости, необходимые для логики календаря
from services.calendar_api import GoogleCalendarAPI
from states.calendar_states import CalendarStates
from datetime import datetime, timedelta
from dateutil import parser

from filters.admin_filter import AdminFilter # Импортируем AdminFilter
from config.settings import ADMIN_IDS, LANGUAGES # Импортируем список ADMIN_IDS и языковые настройки

from states.admin_states import AdminStates # Импортируем состояния администратора
from states.language_states import LanguageStates # Импортируем состояния языка
from utils.i18n import get_text # Импортируем функцию локализации
from utils.i18n import loaded_locales # Импортируем загруженные локали

logger = logging.getLogger(__name__)

router = Router()

# Инициализируем API календаря здесь, так как хендлеры теперь в этом файле
calendar_api = GoogleCalendarAPI()

def escape_markdownv2(text: str) -> str:
    """Escapes characters reserved in MarkdownV2."""
    reserved_chars = r'_*[]()~`>#+-|=|{}.! '
    return re.sub(f'([{re.escape(reserved_chars)}])', r'\\\g<1>', text)

@router.message(Command("start"))
async def cmd_start(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None

    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("command_start_stats")

    if user_id is None:
        logger.error("Не удалось определить user_id в cmd_start.")
        await event.answer(get_text("error_user_id_not_found", user_id, db=db))
        return

    # Проверяем, является ли пользователь администратором
    is_admin = user_id in ADMIN_IDS

    if not is_admin:
        # Если пользователь не администратор (студент), отправляем специфическое приветствие и расписание
        await event.answer(get_text("welcome_student_start", user_id, db=db))
        # Вызываем логику отображения событий на неделю
        await _handle_week_events_logic(event, db, state)
        # Отправляем главное меню
        await event.answer(
            get_text("main_menu", user_id, db=db),
            reply_markup=get_main_keyboard(user_id, db=db)
        )
    else:
        # Если пользователь администратор, используем специфическое приветствие для старосты
        welcome_message = get_text("welcome_admin_start", user_id, db=db)
        await event.answer(
            welcome_message,
            reply_markup=get_main_keyboard(user_id, db=db)
        )

async def send_help_message(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None

    if user_id in ADMIN_IDS:
        response = get_text("help_admin", user_id, db=db)
    else:
        response = get_text("help_student", user_id, db=db)

    await event.answer(response)

@router.message(Command("help"))
async def cmd_help(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_help")
    await send_help_message(event, db, state)

@router.message(F.text == get_text("button_help", None, db=next(get_db())))
async def handle_help_button(event: Message, db: Session, state: FSMContext):
    # Статистика для этой кнопки обрабатывается в handle_unknown
    await send_help_message(event, db, state)

@router.message(Command("stats"), AdminFilter())
async def cmd_stats(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_stats")

    # Используем репозиторий для получения статистики
    all_stats = stats_repo.get_all_statistics()

    if not all_stats:
        await event.answer(get_text("stats_empty", user_id, db=db))
        return

    response = get_text("stats_header", user_id, db=db) + "\n"
    for stat_entry in all_stats:
        button_key = stat_entry.button_key
        count = stat_entry.click_count
        # Получаем локализованное название кнопки, если есть, явно приводя ключ к строке
        button_text = get_text(str(button_key), user_id, db=db)
        # ИЗМЕНЕНИЕ: Добавлен лог для отладки локализации статистики
        logger.info(f"Stats localization check: key='{button_key}', get_text returned='{button_text}'")
        response += get_text("stats_item", user_id, db=db).format(handler_name=button_text, count=count)

    await event.answer(response, parse_mode=ParseMode.MARKDOWN_V2)

@router.message(Command("broadcast"), AdminFilter())
async def cmd_broadcast(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_broadcast")
    await event.answer(get_text("broadcast_prompt", user_id, db=db))
    await state.set_state(AdminStates.waiting_for_broadcast_message)

@router.message(F.text == get_text("button_calendar", None, db=next(get_db())))
async def handle_calendar_button(event: Message, db: Session, state: FSMContext):
    # Статистика для этой кнопки обрабатывается в handle_unknown
    logger.info(f"Button 'Календарь' clicked by user {event.from_user.id if event.from_user else 'N/A'}")
    await cmd_calendar(event, db=db)

@router.message(F.text == get_text("button_create_event", None, db=next(get_db())), AdminFilter())
async def handle_create_event_button(event: Message, db: Session, state: FSMContext):
    # Статистика для этой кнопки обрабатывается в handle_unknown
    user_id = event.from_user.id if event.from_user else None
    await event.answer(get_text("create_event_name_prompt", user_id, db=db))
    await state.set_state(CalendarStates.waiting_for_event_name)

@router.message(F.text == get_text("button_week_events", None, db=next(get_db())))
async def handle_week_events_button(event: Message, db: Session, state: FSMContext):
    # Статистика для этой кнопки обрабатывается в handle_unknown
    user_id = event.from_user.id if event.from_user else None
    logger.info(f"Button 'События на неделю' clicked by user {user_id}. Calling universal handler.")
    incoming_text = event.text
    
    # Ищем обработчик для этой кнопки в BUTTON_HANDLERS
    for key, handler_func in BUTTON_HANDLERS.items():
        localized_text = get_text(key, user_id, db=db)
        if incoming_text == localized_text:
            logger.info(f"Matched button text '{incoming_text}' (key: '{key}') for user {user_id}. Calling handler.")
            
            # Вызываем соответствующий обработчик
            await handler_func(event, db, state)
            return

@router.message(F.text == get_text("button_delete_event", None, db=next(get_db())), AdminFilter())
async def handle_delete_event_button(event: Message, db: Session, state: FSMContext):
    # Статистика для этой кнопки обрабатывается в handle_unknown
    user_id = event.from_user.id if event.from_user else None
    await event.answer(get_text("delete_event_prompt", user_id, db=db))
    await state.set_state(CalendarStates.waiting_for_event_id_to_delete)

@router.message(F.text == get_text("button_back", None, db=next(get_db())))
async def handle_back_button(event: Message, db: Session, state: FSMContext):
    # Статистика для этой кнопки обрабатывается в handle_unknown
    current_state = await state.get_state()
    if current_state:
        logger.info(f"Clearing state: {current_state}")
        await state.clear()
    user_id = event.from_user.id if event.from_user else None

    await event.answer("Главное меню:", reply_markup=get_main_keyboard(user_id, db=db))

@router.message(CalendarStates.waiting_for_event_id_to_delete, AdminFilter())
async def process_event_id_to_delete(event: Message, db: Session, state: FSMContext):
    event_id = event.text
    user_id = event.from_user.id if event.from_user else None

    if not event_id:
        await event.answer(get_text("delete_event_empty_id", user_id, db=db))
        return
    
    success = await calendar_api.delete_event(event_id)
    
    if success:
        await event.answer(get_text("delete_event_success", user_id, db=db).format(event_id=event_id))
    else:
        await event.answer(get_text("delete_event_failed", user_id, db=db).format(event_id=event_id))
        
    await state.clear()
    await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))

@router.message(StateFilter(LanguageStates.waiting_for_language_selection))
async def process_language_selection(event: Message, db: Session, db_user: User, state: FSMContext):
    logger.info(f"User {event.from_user.id if event.from_user else 'N/A'} in waiting_for_language_selection state, received: {event.text}")
    selected_language_name = event.text
    user_id = event.from_user.id if event.from_user else None

    if user_id is None:
        logger.error("Не удалось определить user_id в process_language_selection.")
        await event.answer(get_text("error_user_id_not_found", user_id, db=db))
        await state.clear()
        await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))
        return

    selected_language_code = None
    for code, name in LANGUAGES.items():
        if name == selected_language_name:
            selected_language_code = code
            break

    if selected_language_code and selected_language_code in loaded_locales:
        user_repo = UserRepository(db)
        user_repo.update_user_language(user_id, selected_language_code)
        await event.answer(get_text("language_changed", user_id, db=db).format(language_name=selected_language_name),
                             reply_markup=get_main_keyboard(user_id, db=db))
        logger.info(f"User {user_id} changed language to {selected_language_code} in DB via repository.")
        await state.clear()
        logger.info(f"User {user_id} cleared state after language selection.")
    else:
        await event.answer(get_text("unknown_language", user_id, db=db),
                             reply_markup=get_language_selection_keyboard())
        logger.warning(f"User {user_id} sent unknown or unloaded language name: {selected_language_name}. Current DB language: {db_user.language_code}")
        return

@router.message(StateFilter(AdminStates.waiting_for_broadcast_message), F.text == get_text("button_back_to_main", None, db=next(get_db())), AdminFilter())
async def handle_back_from_broadcast(event: Message, db: Session, state: FSMContext):
    # ИЗМЕНЕНИЕ: Специальный обработчик для кнопки "В главное меню" в состоянии рассылки
    logger.info(f"Admin {event.from_user.id if event.from_user else 'N/A'} pressed 'Back to main menu' button during broadcast.")
    # Вызываем существующую логику возврата в главное меню
    await _handle_back_to_main_logic(event, db, state)

@router.message(StateFilter(AdminStates.waiting_for_broadcast_message), AdminFilter())
async def process_broadcast_message(event: Message, db: Session, bot: Bot, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    
    if not event.text:
        await event.answer(get_text("broadcast_empty", user_id, db=db))
        return

    # ИЗМЕНЕНИЕ: Проверяем, является ли введенный текст текстом кнопки
    incoming_text = event.text
    is_button_text = False
    # Используем словарь BUTTON_HANDLERS для получения ключей кнопок
    for key in BUTTON_HANDLERS.keys():
        # Получаем локализованный текст кнопки. Используем user_id и db из аргументов хендлера.
        localized_text = get_text(key, user_id, db=db)
        if incoming_text == localized_text:
            is_button_text = True
            break

    if is_button_text:
        # Если введен текст кнопки, предупреждаем администратора и остаемся в состоянии
        await event.answer(get_text("broadcast_button_text_error", user_id, db=db))
        # Не сбрасываем состояние, чтобы администратор мог ввести другое сообщение или выйти
        return # Прекращаем выполнение функции, не отправляя рассылку

    # Если введен не текст кнопки, продолжаем рассылку
    user_repo = UserRepository(db) # Получаем репозиторий здесь
    all_users = user_repo.get_all_users()
    # ИЗМЕНЕНИЕ: Преобразуем user.id сначала к str, затем к int
    user_ids_to_broadcast = [int(str(user.id)) for user in all_users]
    logger.info(f"Broadcasting message to {len(user_ids_to_broadcast)} users")

    sent_count = 0
    failed_count = 0

    # Сбрасываем состояние ПЕРЕД отправкой сообщения о завершении и главного меню
    await state.clear()

    for broadcast_user_id in user_ids_to_broadcast:
        try:
            await bot.send_message(
                chat_id=broadcast_user_id,
                text=event.text,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast message to user {broadcast_user_id}: {e}")
            failed_count += 1

    await event.answer(
        get_text("broadcast_complete", user_id, db=db).format(
            sent_count=sent_count,
            failed_count=failed_count
        )
    )

    # Отправляем главное меню после сброса состояния
    await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))

@router.message(StateFilter(CalendarStates.waiting_for_event_name))
async def process_event_name(event: Message, db: Session, state: FSMContext):
    logger.info(f"Processing event name for user {event.from_user.id if event.from_user else 'N/A'} in state waiting_for_event_name")
    user_id = event.from_user.id if event.from_user else None
    event_name = event.text

    if not event_name:
        await event.answer(get_text("create_event_name_empty", user_id, db=db))
        return

    await state.update_data(event_name=event_name)
    await event.answer(get_text("create_event_date_prompt", user_id, db=db))
    await state.set_state(CalendarStates.waiting_for_event_date)

@router.message(StateFilter(CalendarStates.waiting_for_event_date))
async def process_event_date(event: Message, db: Session, state: FSMContext):
    logger.info(f"Processing event date for user {event.from_user.id if event.from_user else 'N/A'} in state waiting_for_event_date")
    user_id = event.from_user.id if event.from_user else None
    event_date_str = event.text

    if not event_date_str:
        await event.answer(get_text("create_event_date_empty", user_id, db=db))
        return

    # Проверяем формат даты ДД.ММ.ГГГГ
    try:
        datetime.strptime(event_date_str, '%d.%m.%Y')
    except ValueError:
        await event.answer(get_text("create_event_date_invalid", user_id, db=db))
        return

    await state.update_data(event_date=event_date_str)
    # ИЗМЕНЕНО: Теперь запрашиваем время после даты
    await event.answer(get_text("create_event_time_prompt", user_id, db=db))
    # ИЗМЕНЕНО: Переходим в состояние ожидания времени
    await state.set_state(CalendarStates.waiting_for_event_time)

@router.message(StateFilter(CalendarStates.waiting_for_event_description))
async def process_event_description(event: Message, db: Session, state: FSMContext):
    # ИЗМЕНЕНО: Эта функция теперь обрабатывает ввод описания и создает событие
    logger.info(f"Processing event description for user {event.from_user.id if event.from_user else 'N/A'} in state waiting_for_event_description")
    user_id = event.from_user.id if event.from_user else None
    event_description = event.text

    user_data = await state.get_data()
    event_name = user_data.get("event_name")
    event_date_str = user_data.get("event_date")
    event_time_str = user_data.get("event_time") # Получаем время из данных состояния

    # Собираем дату и время в datetime объект
    try:
        event_datetime_str = f"{event_date_str} {event_time_str}"
        start_datetime = datetime.strptime(event_datetime_str, '%d.%m.%Y %H:%M')
        # Предполагаем, что событие длится 1 час, можно изменить
        end_datetime = start_datetime + timedelta(hours=1)
    except ValueError as e:
        logger.error(f"Error parsing combined datetime string '{event_datetime_str}': {e}")
        await event.answer(get_text("create_event_datetime_error", user_id, db=db))
        await state.clear()
        await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))
        return

    # Вызываем API календаря для создания события
    try:
        created_event = await calendar_api.create_event(
            summary=str(event_name), # Приведение к str
            start_time=start_datetime,
            end_time=end_datetime,
            description=str(event_description) # Приведение к str для устранения ошибки линтера
        )

        if created_event:
            await event.answer(get_text("create_event_success", user_id, db=db).format(
                summary=created_event.get('summary', 'N/A'),
                start_time=start_datetime.strftime('%d.%m.%Y %H:%M'), # Форматируем дату и время
                end_time=end_datetime.strftime('%d.%m.%Y %H:%M'),   # Форматируем дату и время
                description=created_event.get('description', 'Нет описания')
            ))
        else:
            await event.answer(get_text("create_event_api_error", user_id, db=db))

    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        await event.answer(get_text("create_event_api_error", user_id, db=db))

    await state.clear()
    await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))

@router.message(StateFilter(CalendarStates.waiting_for_event_time))
async def process_event_time(event: Message, db: Session, state: FSMContext):
    # ИЗМЕНЕНО: Эта функция теперь обрабатывает ввод времени и запрашивает описание
    logger.info(f"Processing event time for user {event.from_user.id if event.from_user else 'N/A'} in state waiting_for_event_time")
    user_id = event.from_user.id if event.from_user else None
    event_time_str = event.text

    if not event_time_str:
        await event.answer(get_text("create_event_time_empty", user_id, db=db))
        return

    # Проверяем формат времени ЧЧ:ММ
    try:
        datetime.strptime(event_time_str, '%H:%M')
    except ValueError:
        await event.answer(get_text("create_event_time_invalid", user_id, db=db))
        return

    await state.update_data(event_time=event_time_str) # Сохраняем время в данные состояния
    await event.answer(get_text("create_event_description_prompt", user_id, db=db)) # Запрашиваем описание
    await state.set_state(CalendarStates.waiting_for_event_description) # Переходим в состояние ожидания описания

class CalendarEvent(TypedDict):
    id: str
    summary: str
    description: Optional[str]
    start: Dict[str, str]

@router.message()
async def handle_unknown(event: Message, db: Session, state: FSMContext):
    # Получаем текущее состояние
    current_state = await state.get_state()

    # Если находимся в состоянии, связанном с календарем, игнорируем это сообщение
    if current_state and current_state.startswith('CalendarStates.'):
        logger.info(f"Ignoring message in CalendarStates from user {event.from_user.id if event.from_user else 'N/A'}")
        return

    if not event.text:
        return

    user_id = event.from_user.id if event.from_user else None
    incoming_text = event.text

    # Ищем, соответствует ли входящий текст какой-либо локализованной кнопке
    for key, handler_func in BUTTON_HANDLERS.items():
        localized_text = get_text(key, user_id, db=db)
        if incoming_text == localized_text:
            logger.info(f"Matched button text '{incoming_text}' (key: '{key}') for user {user_id}. Calling handler.")

            # Используем репозиторий для инкрементации статистики
            stats_repo = ButtonStatisticRepository(db)
            stats_repo.increment_button_click(key) # Статистика инкрементируется здесь для кнопок, пойманных handle_unknown
            logger.info(f"Button '{key}' clicked. Statistics updated in DB.")

            # Вызываем соответствующий обработчик
            await handler_func(event, db, state) # Передаем event, db и state
            return

    # Если текст не соответствует ни одной кнопке и не в состоянии календаря, выполняем стандартную логику unknown
    logger.info(f"Unknown message received from user {user_id} with text: '{incoming_text}'")
    await event.answer(
        get_text("main_menu", user_id, db=db),
        reply_markup=get_main_keyboard(user_id, db=db)
    )


# Вспомогательные функции для логики кнопок
async def _handle_language_button_logic(event: Message, db: Session, state: FSMContext):
    logger.info(f"User {event.from_user.id if event.from_user else 'N/A'} clicked Language button via universal handler.")
    user_id = event.from_user.id if event.from_user else None

    if user_id is None:
        logger.error("Не удалось определить user_id в _handle_language_button_logic.")
        await event.answer(get_text("error_user_id_not_found", user_id, db=db))
        await state.clear()
        await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))
        return

    await event.answer(
        get_text("choose_language", user_id, db=db),
        reply_markup=get_language_selection_keyboard()
    )
    await state.set_state(LanguageStates.waiting_for_language_selection)

async def _handle_create_event_logic(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    
    if user_id is None or user_id not in ADMIN_IDS:
        await event.answer(get_text("feature_for_students_only", user_id, db=db))
        return
        
    await event.answer(
        get_text("create_event_instructions", user_id, db=db),
        reply_markup=get_main_keyboard(user_id, db=db)
    )
    await state.set_state(CalendarStates.waiting_for_event_name)

async def _handle_week_events_logic(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    events: List[Dict[str, Any]] = await calendar_api.get_events(days=7)

    if not events:
        await event.answer(get_text("week_events_empty", user_id, db=db))
        return

    response = get_text("week_events_header", user_id, db=db)
    for event_data in events:
        # Экранируем только сам текст summary и description
        summary_escaped = escape_markdownv2(event_data['summary'])
        description_escaped = escape_markdownv2(event_data.get('description', get_text("no_description", user_id, db=db)))

        # Форматируем время и затем экранируем его
        start = parser.parse(event_data['start'].get('dateTime', event_data['start'].get('date')))
        formatted_time = start.strftime('%d.%m.%Y %H:%M')
        formatted_time_escaped = escape_markdownv2(formatted_time) # Экранируем форматированное время

        # ID события не нуждается в экранировании, так как будет в моноширинном блоке
        event_id = event_data['id']

        response += get_text("week_events_item", user_id, db=db).format(
            summary=summary_escaped,
            formatted_time=formatted_time_escaped, # Используем экранированное время
            description=description_escaped,
            event_id=event_id
        )

    await event.answer(response, parse_mode=ParseMode.MARKDOWN_V2)

async def _handle_delete_event_logic(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    
    if user_id is None or user_id not in ADMIN_IDS:
        await event.answer(get_text("feature_for_students_only", user_id, db=db))
        return
        
    await event.answer(
        get_text("delete_event_instructions", user_id, db=db),
        reply_markup=get_main_keyboard(user_id, db=db)
    )
    await state.set_state(CalendarStates.waiting_for_event_id_to_delete)

async def _handle_back_logic(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    
    await state.clear()
    await event.answer(
        get_text("main_menu", user_id, db=db),
        reply_markup=get_main_keyboard(user_id, db=db)
    )

async def _handle_admin_menu_logic(event: Message, db: Session, state: FSMContext):
    user_id = event.from_user.id if event.from_user else None
    
    if user_id is None or user_id not in ADMIN_IDS:
        await event.answer(get_text("feature_for_students_only", user_id, db=db))
        return
        
    await event.answer(
        get_text("admin_menu", user_id, db=db),
        reply_markup=get_admin_keyboard(user_id, db=db)
    )

async def _handle_back_to_main_logic(event: Message, db: Session, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        logger.info(f"Clearing state: {current_state}")
        if current_state == AdminStates.waiting_for_broadcast_message:
            user_id = event.from_user.id if event.from_user else None
            await event.answer(get_text("broadcast_cancelled", user_id, db=db))
            logger.info(f"Broadcast cancelled by user {user_id}")
        await state.clear()

    user_id = event.from_user.id if event.from_user else None
    await event.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))

# Вспомогательные функции-обертки для хендлеров кнопок
async def _wrap_cmd_calendar(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_calendar") # Регистрируем статистику для кнопки
    await cmd_calendar(event, db=db)

async def _wrap_send_help_message(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_help") # Регистрируем статистику для кнопки
    await send_help_message(event, db, state)

async def _wrap_handle_language_button_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_language") # Регистрируем статистику для кнопки
    await _handle_language_button_logic(event, db, state)

async def _wrap_handle_create_event_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_create_event") # Регистрируем статистику для кнопки
    await _handle_create_event_logic(event, db, state)

async def _wrap_handle_week_events_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_week_events") # Регистрируем статистику для кнопки
    await _handle_week_events_logic(event, db, state)

async def _wrap_handle_delete_event_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_delete_event") # Регистрируем статистику для кнопки
    await _handle_delete_event_logic(event, db, state)

async def _wrap_handle_back_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_back") # Регистрируем статистику для кнопки
    await _handle_back_logic(event, db, state)

async def _wrap_handle_admin_menu_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_admin_menu") # Регистрируем статистику для кнопки
    await _handle_admin_menu_logic(event, db, state)

async def _wrap_handle_back_to_main_logic(event: Message, db: Session, state: FSMContext):
    stats_repo = ButtonStatisticRepository(db)
    stats_repo.increment_button_click("button_back_to_main") # Регистрируем статистику для кнопки
    await _handle_back_to_main_logic(event, db, state)

async def _wrap_cmd_stats(event: Message, db: Session, state: FSMContext):
    # Статистика для этой команды обрабатывается в cmd_stats
    await cmd_stats(event, db, state)

async def _wrap_cmd_broadcast(event: Message, db: Session, state: FSMContext):
    # Статистика для этой команды обрабатывается в cmd_broadcast
    await cmd_broadcast(event, db, state)

# Словарь соответствия ключей кнопок и обработчиков
BUTTON_HANDLERS = {
    "button_calendar": _wrap_cmd_calendar,
    "button_help": _wrap_send_help_message,
    "button_language": _wrap_handle_language_button_logic,
    "button_create_event": _wrap_handle_create_event_logic,
    "button_week_events": _wrap_handle_week_events_logic,
    "button_delete_event": _wrap_handle_delete_event_logic,
    "button_back": _wrap_handle_back_logic,
    "button_admin_menu": _wrap_handle_admin_menu_logic,
    "button_back_to_main": _wrap_handle_back_to_main_logic,
    "button_stats": _wrap_cmd_stats,
    "button_broadcast": _wrap_cmd_broadcast,
}

# Словарь для хранения статистики нажатий кнопок: { 'ключ_кнопки': количество_нажатий }
# button_statistics: Dict[str, int] = {} 