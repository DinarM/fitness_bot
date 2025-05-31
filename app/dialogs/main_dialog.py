from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start, Row
from aiogram_dialog.widgets.text import Const, Format

from app.getters.main_getters import admin_flag_visible, main_getter
# from app.handlers.main_handlers import on_click_test_start
from app.dialogs import states


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
                    # on_click=on_click_test_start
                ),
                Start(
                    text=Const("🏋️‍♂️ Тренировки"),
                    id="training",
                    state=states.Multiwidget.MAIN,  # или нужный state для тренировок
                ),
                Start(
                    text=Const("🔐 Админка"),
                    id="admin",
                    state=states.Admin.MAIN,  # или нужный state для тренировок
                    when=admin_flag_visible
                ),
            ),
            state=states.Main.MAIN,
            getter=main_getter,
            parse_mode="HTML",
        ),
        launch_mode=LaunchMode.ROOT,
    )
