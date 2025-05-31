from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from app.dialogs.common import MAIN_MENU_BUTTON

from app.dialogs import states


admin_window = Window(
    Const('Главное меню администратора:'),
    Start(
        text=Const("Пользователи"),
        id="users",
        state=states.Users.MAIN,
    ),
    MAIN_MENU_BUTTON,
    state=states.Admin.MAIN,
    parse_mode='HTML',
)

admin_dialog = Dialog(admin_window)