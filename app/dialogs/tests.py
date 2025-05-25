from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db_utils.utils import get_test_types
from app.db.models import TestType, BotToken

from . import states

from aiogram_dialog import DialogManager, StartMode
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode


async def on_test_type_click(c: CallbackQuery, widget, manager: DialogManager, item: int):
    # Сохраняем выбранный тип теста
    # await manager.dialog_data.update({"test_type_id": item["id"]})
    print(f"🌀 📝 Тестирование нажата {item}")
    # Переходим в окно вопросов
    await manager.start(
        states.TestsSG.START_WINDOW,
        # mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
        data={"test_type_id": item},
    )



test_selection_window = Window(
    Const("Выберите тип тестирования:"),
    Select(
        Format("🔹 {item[name]}"),
        id="test_type_select",
        item_id_getter=lambda item: item["id"],
        items="test_types",
        on_click=on_test_type_click,
    ),
    getter=get_test_types,
    # on_start=on_start_tests,
    state=states.Tests.MAIN,
)

test_dialog = Dialog(test_selection_window)