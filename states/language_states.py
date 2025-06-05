# states/language_states.py

from aiogram.fsm.state import State, StatesGroup

class LanguageStates(StatesGroup):
    waiting_for_language_selection = State() 