from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy import select
from db import AsyncSessionLocal
from db_utils.utils import get_test_types
from models import TestType, BotToken

from . import states

from aiogram_dialog import DialogManager, StartMode




test_selection_window = Window(
    Const("Выберите тип тестирования:"),
    Select(
        Format("🔹 {item[name]}"),
        id="test_type_select",
        item_id_getter=lambda item: item["id"],
        items="test_types",

    ),
    getter=get_test_types,
    # on_start=on_start_tests,
    state=states.Tests.MAIN,
)

test_dialog = Dialog(test_selection_window)