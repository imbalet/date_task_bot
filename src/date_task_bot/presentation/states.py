from aiogram.fsm.state import State, StatesGroup


class TimezoneSelectionState(StatesGroup):
    AWAIT_TZ_NAME = State()
