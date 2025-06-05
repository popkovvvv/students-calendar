import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from dateutil import parser
from typing import Optional, Dict, Any

from services.calendar_api import GoogleCalendarAPI
from states.calendar_states import CalendarStates
from keyboards.inline import get_calendar_keyboard, get_event_actions_keyboard
from keyboards.reply import get_main_keyboard, get_calendar_reply_keyboard
from utils.i18n import get_text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = Router()
calendar_api = GoogleCalendarAPI()

@router.message(Command("calendar"))
async def cmd_calendar(message: Message, db: Session, user_id: Optional[int] = None):
    if user_id is None and message.from_user:
        user_id = message.from_user.id

    if user_id is None:
        logger.error("Не удалось определить user_id в cmd_calendar.")
        await message.answer(get_text("error_user_id_not_found", user_id, db=db))
        return

    await message.answer(
        get_text("calendar_menu", user_id, db=db),
        reply_markup=get_calendar_reply_keyboard(user_id, db=db)
    )

@router.message(CalendarStates.waiting_for_event_name)
async def process_event_name(message: Message, db: Session, state: FSMContext):
    logger.info(f"Received message in waiting_for_event_name state: {message.text}")
    user_id = message.from_user.id if message.from_user else None
    if message.text:
        await state.update_data(event_name=message.text)
        await message.answer(
            get_text("create_event_date_prompt", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        await state.set_state(CalendarStates.waiting_for_event_date)

@router.message(CalendarStates.waiting_for_event_date)
async def process_event_date(message: Message, db: Session, state: FSMContext):
    user_id = message.from_user.id if message.from_user else None
    if not message.text:
        await message.answer(
            get_text("create_event_date_empty", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        return
        
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(event_date=date)
        await message.answer(
            get_text("create_event_time_prompt", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        await state.set_state(CalendarStates.waiting_for_event_time)
    except ValueError:
        await message.answer(
            get_text("create_event_date_invalid", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )

@router.message(CalendarStates.waiting_for_event_time)
async def process_event_time(message: Message, db: Session, state: FSMContext):
    user_id = message.from_user.id if message.from_user else None
    if not message.text:
        await message.answer(
            get_text("create_event_time_empty", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        return
        
    try:
        time = datetime.strptime(message.text, "%H:%M").time()
        data = await state.get_data()
        date = data["event_date"]
        start_time = datetime.combine(date.date(), time)
        await state.update_data(start_time=start_time)
        await message.answer(
            get_text("create_event_duration_prompt", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        await state.set_state(CalendarStates.waiting_for_event_duration)
    except ValueError:
        await message.answer(
            get_text("create_event_time_invalid", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )

@router.message(CalendarStates.waiting_for_event_duration)
async def process_event_duration(message: Message, db: Session, state: FSMContext):
    user_id = message.from_user.id if message.from_user else None
    if not message.text:
        await message.answer(
            get_text("create_event_duration_invalid", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        return
        
    try:
        duration = float(message.text)
        data = await state.get_data()
        start_time = data["start_time"]
        end_time = start_time + timedelta(hours=duration)
        await state.update_data(end_time=end_time)
        await message.answer(
            get_text("create_event_description_prompt", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
        await state.set_state(CalendarStates.waiting_for_event_description)
    except ValueError:
        await message.answer(
            get_text("create_event_duration_invalid", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )

@router.message(CalendarStates.waiting_for_event_description)
async def process_event_description(message: Message, db: Session, state: FSMContext):
    user_id = message.from_user.id if message.from_user else None
    data = await state.get_data()
    description = message.text if message.text is not None and message.text != "-" else get_text("no_description", user_id, db=db)
    
    logger.info(f"Attempting to create event with data: {data}")
    
    event = await calendar_api.create_event(
        summary=data["event_name"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        description=description if description != get_text("no_description", user_id, db=db) else ""
    )
    
    if event:
        await message.answer(
            get_text("create_event_success", user_id, db=db).format(
                summary=event['summary'],
                start_time=parser.parse(event['start']['dateTime']).strftime('%d.%m.%Y %H:%M'),
                end_time=parser.parse(event['end']['dateTime']).strftime('%H:%M'),
                description=event.get('description', get_text("no_description", user_id, db=db))
            ),
            reply_markup=get_main_keyboard(user_id, db=db)
        )
    else:
        await message.answer(
            get_text("create_event_failed", user_id, db=db),
            reply_markup=get_calendar_reply_keyboard(user_id, db=db)
        )
    
    await state.clear()
    if event:
        await message.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db))
    else:
        await message.answer(get_text("main_menu", user_id, db=db), reply_markup=get_main_keyboard(user_id, db=db)) 