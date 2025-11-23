from aiogram.fsm.state import State, StatesGroup


class TimezoneSelectionState(StatesGroup):
    AWAIT_TZ_NAME = State()


class TaskEditingState(StatesGroup):
    AWAIT_DUE_DATE = State()
    AWAIT_TEXT = State()
