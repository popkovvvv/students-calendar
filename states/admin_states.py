# states/admin_states.py

from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State() 