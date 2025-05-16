from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from . import states


def create_main_dialog() -> Dialog:
    return Dialog(
        Window(
            Format("👋 Привет, {event.from_user.first_name}!"),
            Const(
                "Я твой персональный бот-тренер 🤖💪\n"
                "Помогу оценить твой уровень, поставить цели и подобрать эффективные тренировки.\n\n"
                "📌 Чтобы начать, пройди первичное тестирование — нажми кнопку <b>📝 Тестирование</b> ниже.\n"
                "Это поможет мне понять, какие упражнения подойдут именно тебе.\n\n"
                "🗂 Индивидуальную программу ты найдешь в разделе <b>🏋️‍♂️ Тренировки</b>."
                ),
            Row(
                Start(
                    text=Const("📝 Тестирование"),
                    id="test",
                    state=states.Tests.MAIN,  # или другой state, если он у тебя для теста
                ),
                Start(
                    text=Const("🏋️‍♂️ Тренировки"),
                    id="training",
                    state=states.Multiwidget.MAIN,  # или нужный state для тренировок
                ),
            ),
            # markup_factory=ReplyKeyboardFactory(
            #     input_field_placeholder=Format("{event.from_user.username}"),
            #     resize_keyboard=True,
            # ),
            state=states.Main.MAIN,
            parse_mode="HTML",
        ),
        launch_mode=LaunchMode.ROOT,
    )
