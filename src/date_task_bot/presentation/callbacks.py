from aiogram.filters.callback_data import CallbackData


class BackCallback(CallbackData, prefix="back"):
    pass


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class ConfirmCallback(CallbackData, prefix="confirm"):
    pass
