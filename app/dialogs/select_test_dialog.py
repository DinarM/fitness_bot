from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format

from app.handlers.select_test_handlers import on_test_type_click
from app.getters.select_test_getters import get_test_types_for_dialog

from app.dialogs import states


test_selection_window = Window(
    Const("Выберите тип тестирования:"),
    Select(
        Format("🔹 {item[name]}"),
        id="test_type_select",
        item_id_getter=lambda item: item["id"],
        items="test_types",
        on_click=on_test_type_click,
    ),
    getter=get_test_types_for_dialog,
    state=states.Tests.MAIN,
)

test_dialog = Dialog(test_selection_window)