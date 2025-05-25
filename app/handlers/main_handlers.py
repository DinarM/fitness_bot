from app.dialogs import states
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

async def on_click_test_start(callback: CallbackQuery, button, manager: DialogManager):
    await manager.start(states.Tests.MAIN, mode=StartMode.RESET_STACK)
    await callback.answer()