from aiogram.fsm.state import State, StatesGroup

class CalendarStates(StatesGroup):
    waiting_for_event_name = State()
    waiting_for_event_date = State()
    waiting_for_event_time = State()
    waiting_for_event_duration = State()
    waiting_for_event_description = State()
    waiting_for_event_id_to_delete = State() 