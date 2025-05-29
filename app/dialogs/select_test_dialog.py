from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.common import MAIN_MENU_BUTTON
from app.handlers.select_test_handlers import on_test_type_click
from app.getters.select_test_getters import get_test_types_for_dialog

from app.dialogs import states


test_selection_window = Window(
    Const('Выберите тип тестирования:'),
    # Если нет тестов, показываем текст вместо кнопок
    Format('\n<b>{no_tests_text}</b>', when=lambda data, *_: not data.get('test_types')),
    Select(
        Format('🔹 {item[name]}'),
        id='test_type_select',
        item_id_getter=lambda item: item['id'],
        items='test_types',
        on_click=on_test_type_click,
        when=lambda data, *_: data.get('test_types'),
    ),
    MAIN_MENU_BUTTON,
    getter=get_test_types_for_dialog,
    state=states.Tests.MAIN,
    parse_mode='HTML',
)

test_dialog = Dialog(test_selection_window)