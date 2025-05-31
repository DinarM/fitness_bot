from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.common import MAIN_MENU_BUTTON


from app.dialogs import states
from app.getters.admin_users_getters import get_admin_users


user_selection_window = Window(
    Const('Пользователи:'),
    # Если нет тестов, показываем текст вместо кнопок
    Format('\n<b>{no_users_text}</b>', when=lambda data, *_: not data.get('users')),
    Select(
        Format('🔹 {item[name]}'),
        id='user_select',
        item_id_getter=lambda item: item['id'],
        items='users',
        # on_click=on_test_type_click,
        when=lambda data, *_: data.get('users'),
    ),
    MAIN_MENU_BUTTON,
    getter=get_admin_users,
    state=states.Users.MAIN,
    parse_mode='HTML',
)

users_dialog = Dialog(user_selection_window)