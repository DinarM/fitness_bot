from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.kbd import Button

from . import states
from aiogram_dialog.about import about_aiogram_dialog_button
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

async def on_click_test_start(callback: CallbackQuery, button, manager: DialogManager):
    print("🌀 📝 Тестирование нажата")
    # Запускаем тестовый диалог вручную
    await manager.start(states.Tests.MAIN, mode=StartMode.RESET_STACK)
    # Подтверждаем получение нажатия
    await callback.answer()

# def create_main_dialog() -> Dialog:
#     return Dialog(
main_dialog = Dialog(
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
                    state=states.Tests.MAIN,
                ),
                Start(
                    text=Const("🏋️‍♂️ Тренировки"),
                    id="training",
                    state=states.Multiwidget.MAIN,  # или нужный state для тренировок
                ),
                Start(
                    text=Const("☑️ Selection widgets"),
                    id="selects",
                    state=states.Selects.MAIN,
                ),
            ),
            # markup_factory=ReplyKeyboardFactory(
            #     input_field_placeholder=Format("{event.from_user.username}"),
            #     resize_keyboard=True,
            # ),
            # about_aiogram_dialog_button(),
            state=states.Main.MAIN,
            parse_mode="HTML",
        ),
        launch_mode=LaunchMode.ROOT,
    )
