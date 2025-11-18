from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from date_task_bot.presentation.callbacks import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
)
from date_task_bot.presentation.constants.text import MsgKey


class InlineKeyboardFactory:
    def __init__(self, row_width: int = 2):
        self._keyboard: list[list[InlineKeyboardButton]] = []
        self._current_row: list[InlineKeyboardButton] = []
        self._row_width = row_width

    def _flush_row(self) -> "InlineKeyboardFactory":
        """Flushes the current row and starts a new one."""
        if self._current_row:
            self._keyboard.append(self._current_row)
            self._current_row = []
        return self

    def buttons_tuple(
        self, *buttons: tuple[MsgKey, CallbackData]
    ) -> "InlineKeyboardFactory":
        """Adds buttons from tuples.

        Args:
            *buttons (tuple[MsgKey, CallbackData]): tuples with text and callback.

        """
        for text, callback in buttons:
            self.button(text=text, callback_data=callback)
        return self

    def buttons_text_tuple(
        self, *buttons: tuple[str, CallbackData]
    ) -> "InlineKeyboardFactory":
        """Adds buttons from tuples.

        Args:
            *buttons (tuple[str, CallbackData]): tuples with text and callback.

        """
        for text, callback in buttons:
            self.button_text(text=text, callback_data=callback)
        return self

    def buttons(self, *buttons: InlineKeyboardButton) -> "InlineKeyboardFactory":
        """Adds buttons.

        Args:
            *buttons (InlineKeyboardButton): button objects.
        """
        for btn in buttons:
            self._current_row.append(btn)
            if len(self._current_row) >= self._row_width:
                self._flush_row()
        return self

    def button(
        self,
        text: MsgKey,
        callback_data: CallbackData,
        **kwargs,
    ) -> "InlineKeyboardFactory":
        """Adds a single button to the current row.

        Args:
            text (MsgKey): text of the button.
            cbdata (CallbackData): callback of the button.
        """
        btn = InlineKeyboardButton(
            text=text, callback_data=callback_data.pack(), **kwargs
        )
        self._current_row.append(btn)
        if len(self._current_row) >= self._row_width:
            self._flush_row()

        return self

    def button_text(
        self,
        text: str,
        callback_data: CallbackData,
        **kwargs,
    ) -> "InlineKeyboardFactory":
        """Adds a single button with pure text to the current row.

        Args:
            text (MsgKey): text of the button.
            cbdata (CallbackData): callback of the button.
        """
        btn = InlineKeyboardButton(
            text=text, callback_data=callback_data.pack(), **kwargs
        )
        self._current_row.append(btn)
        if len(self._current_row) >= self._row_width:
            self._flush_row()

        return self

    def row_buttons(self, *buttons: InlineKeyboardButton) -> "InlineKeyboardFactory":
        """Flushes the current row and adds a new row of buttons.

        Args:
            *buttons (InlineKeyboardButton): button objects.
        """
        if self._current_row:
            self._flush_row()

        if buttons:
            self._keyboard.append(list(buttons))
        return self

    def row_buttons_tuple(
        self, *buttons: tuple[MsgKey, CallbackData]
    ) -> "InlineKeyboardFactory":
        """Flushes the current row and adds a new row of buttons from tuples.

        Args:
            *buttons (tuple[str, CallbackData]): tuples with text and callback.
        """
        if self._current_row:
            self._flush_row()

        if buttons:
            self._keyboard.append(
                [
                    InlineKeyboardButton(text=text, callback_data=callback.pack())
                    for text, callback in buttons
                ]
            )
        return self

    def as_markup(self) -> InlineKeyboardMarkup:
        """Returns the inline keyboard markup."""
        self._flush_row()
        return InlineKeyboardMarkup(inline_keyboard=self._keyboard)


class KeyboardBuilder(InlineKeyboardFactory):

    def __init__(
        self,
        row_width: int = 2,
        add_back_button: bool = False,
        add_cancel_button: bool = False,
        add_confirm_button: bool = False,
        extra_buttons: list[tuple[MsgKey, CallbackData]] | None = None,
    ):
        super().__init__(row_width)
        self._back_btn = add_back_button
        self._cancel_btn = add_cancel_button
        self._confirm_btn = add_confirm_button
        self._extra_btns = extra_buttons or []

    def conf(
        self,
        row_width: int = 2,
        add_back_button: bool = False,
        add_cancel_button: bool = False,
        add_confirm_button: bool = False,
        extra_buttons: list[tuple[MsgKey, CallbackData]] | None = None,
    ):
        self._row_width = row_width
        self._back_btn = add_back_button
        self._cancel_btn = add_cancel_button
        self._confirm_btn = add_confirm_button
        self._extra_btns = extra_buttons or []
        return self

    def as_markup(self) -> InlineKeyboardMarkup:
        service_buttons: list[tuple[MsgKey, CallbackData]] = []
        if self._back_btn:
            service_buttons.append((MsgKey.BACK, BackCallback()))
        if self._cancel_btn:
            service_buttons.append((MsgKey.CANCEL, CancelCallback()))
        if self._confirm_btn:
            service_buttons.append((MsgKey.CONFIRM, ConfirmCallback()))
        self.row_buttons_tuple(*service_buttons)
        self.row_buttons_tuple(*self._extra_btns)
        return super().as_markup()

    @staticmethod
    def markup(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            return self.as_markup()

        return wrapper
