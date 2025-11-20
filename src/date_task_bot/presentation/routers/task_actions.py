from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from date_task_bot.presentation.callbacks import (
    TaskAction,
    TaskActionCallback,
    TaskPaginationCallback,
)
from date_task_bot.presentation.constants import TEXTS, MsgKey
from date_task_bot.presentation.utils import (
    CallbackQueryWithMessage,
    KeyboardBuilder,
    update_main_message,
)
from date_task_bot.use_cases import DeleteTaskUseCase

router = Router(name=__name__)


@router.callback_query(TaskActionCallback.filter(F.act == TaskAction.DELETE))
async def delete(
    callback: CallbackQueryWithMessage,
    callback_data: TaskActionCallback,
    state: FSMContext,
    chat_id: str,
    kbr_builder: KeyboardBuilder,
    delete_task_uc: DeleteTaskUseCase,
):
    await delete_task_uc.execute(task_id=callback_data.id, user_id=str(chat_id))

    kbr_builder.button(MsgKey.BACK, TaskPaginationCallback(page=1))

    await update_main_message(
        state=state,
        event=callback,
        text=TEXTS[MsgKey.TASK_DELETED],
        reply_markup=kbr_builder.as_markup(),
    )
