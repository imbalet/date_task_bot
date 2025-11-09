from enum import Enum


class MsgKey(str, Enum):
    CANCEL = "cancel"
    BACK = "back"
    CONFIRM = "confirm"


TEXT: dict[MsgKey, str] = {
    MsgKey.CANCEL: "Отмена",
    MsgKey.BACK: "Назад",
    MsgKey.CONFIRM: "Готово",
}
