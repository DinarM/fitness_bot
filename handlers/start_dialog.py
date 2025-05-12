# from aiogram import Dispatcher
# from aiogram_dialog import Dialog, Window
# from aiogram_dialog.widgets.kbd import Button, Row, RequestContact
# from aiogram_dialog.widgets.text import Const
# from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
# from aiogram.fsm.state import StatesGroup, State


# class StartSG(StatesGroup):
#     ask_contact = State()
#     main_menu = State()


# async def on_contact(c, button, dialog_manager):
#     # здесь можно сохранить контакт: c.from_user.id, c.from_user.phone_number
#     await dialog_manager.switch_to(StartSG.main_menu)


# async def on_menu_click(c, button, dialog_manager, **kwargs):
#     choice = button.widget_id  # "test" или "workout"
#     if choice == "test":
#         await c.message.answer("Запускаем тест…")
#         # тут можно вызвать переход в ваш тестовый хендлер
#     else:
#         await c.message.answer("Переходим к тренировкам…")
#         # тут можно вызвать логику тренировок


# ask_contact_window = Window(
#     Const("👋 Добро пожаловать! Пожалуйста, поделитесь своим контактом:"),
#     RequestContact(Const("📲 Поделиться контактом")),
#     state=StartSG.ask_contact,
#     markup_factory=ReplyKeyboardFactory(resize_keyboard=True),
# )

# main_menu_window = Window(
#     Const("Выберите действие:"),
#     Row(
#         Button(Const("📝 Тестирование"), id="test", on_click=on_menu_click),
#         Button(Const("💪 Тренировки"),   id="workout", on_click=on_menu_click),
#     ),
#     state=StartSG.main_menu,
# )

# start_dialog = Dialog(
#     ask_contact_window,
#     main_menu_window,
# )
