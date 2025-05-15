from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.about import about_aiogram_dialog_button
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import (
    RequestContact,
    Row,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
# from handlers.start_dialog import on_contact

from . import states


def create_main_dialog() -> Dialog:
    return Dialog(
        Window(
            Const("👋 Добро пожаловать!"),
            Const("Для начала поделитесь своим контактом, чтобы тренер мог понять с кем работает."),
            Const("После этого вы сможете начать тестирование или тренировки."),
            Row(
                RequestContact(Const("👤 Send contact")),
            ),
            Start(
                text=Const("📜 Scrolling widgets"),
                id="scrolls",
                state=states.Scrolls.MAIN,
            ),
            Start(
                text=Const("☑️ Selection widgets"),
                id="selects",
                state=states.Selects.MAIN,
            ),
            Start(
                text=Const("📅 Calendar"),
                id="cal",
                state=states.Calendar.MAIN,
            ),
            Start(
                text=Const("💯 Counter and Progress"),
                id="counter",
                state=states.Counter.MAIN,
            ),
            Start(
                text=Const("🎛 Combining widgets"),
                id="multiwidget",
                state=states.Multiwidget.MAIN,
            ),
            Start(
                text=Const("🔢 Multiple steps"),
                id="switch",
                state=states.Switch.MAIN,
            ),
            Start(
                text=Const("🔗 Link Preview"),
                id="linkpreview",
                state=states.LinkPreview.MAIN,
            ),
            Start(
                text=Const("⌨️ Reply keyboard"),
                id="reply",
                state=states.ReplyKeyboard.MAIN,
            ),
            about_aiogram_dialog_button(),
            markup_factory=ReplyKeyboardFactory(
                input_field_placeholder=Format("{event.from_user.username}"),
                resize_keyboard=True,
            ),
            state=states.Main.MAIN,
        ),
        launch_mode=LaunchMode.ROOT,
    )

