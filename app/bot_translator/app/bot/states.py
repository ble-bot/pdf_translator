from aiogram.fsm.state import State, StatesGroup


class TranslationStates(StatesGroup):
    waiting_for_language = State()
    processing = State()
