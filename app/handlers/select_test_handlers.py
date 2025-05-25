

from app.dialogs import states

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode


async def on_test_type_click(callback: CallbackQuery, _, manager: DialogManager, item: int):
    await manager.start(
        states.TestsSG.START_WINDOW,
        show_mode=ShowMode.SEND,
        data={"test_type_id": item},
    )
    await callback.answer()