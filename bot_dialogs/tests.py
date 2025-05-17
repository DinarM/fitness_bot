from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy import select
from db import AsyncSessionLocal
from models import TestType, BotToken

from . import states

from aiogram_dialog import DialogManager, StartMode

async def on_start_tests(dialog_manager: DialogManager, **kwargs):
    print("✅ Вход в диалог тестирования")

async def on_click_test_type(callback, select, manager):
    print(f"➡️ Выбран пункт: {callback.data}")
    await callback.message.answer(f"Вы выбрали тест: {callback.data}")

async def get_test_types(dialog_manager, **kwargs):
    print(f"вызов get_test_types с аргументами: {kwargs}")
    async with AsyncSessionLocal() as session:
        telegram_bot_id = dialog_manager.event.bot.id
        result = await session.execute(
            select(BotToken).where(BotToken.telegram_bot_id == telegram_bot_id)
        )
        bot_token = result.scalar_one_or_none()
        if not bot_token:
            return {"test_types": []}

        test_types_result = await session.execute(
            select(TestType).where(TestType.bot_id == bot_token.id)
        )
        test_types = test_types_result.scalars().all()
        return {
            "test_types": [
                {"id": str(tt.id), "name": tt.name} for tt in test_types
            ]
        }

test_selection_window = Window(
    Const("Выберите тип тестирования:"),
    Select(
        Format("🔹 {item[name]}"),
        id="test_type_select",
        item_id_getter=lambda item: item["id"],
        items="test_types",
        on_click=on_click_test_type,
    ),
    getter=get_test_types,
    # on_start=on_start_tests,
    state=states.Tests.MAIN,
)

test_dialog = Dialog(test_selection_window)