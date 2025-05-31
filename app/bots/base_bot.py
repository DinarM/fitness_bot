import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, Message, ReplyKeyboardRemove
from app.dialogs import states
from app.dialogs.main_dialog import main_dialog
from app.dialogs.select_test_dialog import test_dialog
from app.dialogs.tests_flow_dialog import tests_dialog
from app.dialogs.admin_dialog import admin_dialog
from app.dialogs.admin_users_dialog import users_dialog
from app.repo import user_repo, bot_repo
from aiogram_dialog import DialogManager, ShowMode, StartMode, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent


class BaseBot:
    def __init__(self, token_env_name: str):
        self.token_env_name = token_env_name
        self.dialog_router = Router()
        self.dialog_router.include_routers(
            main_dialog,
            test_dialog,
            tests_dialog,
            admin_dialog,
            users_dialog,
        )

    async def start(self, message: Message, dialog_manager: DialogManager):
        """Обработчик команды /start"""
        await user_repo.get_or_create_user(
            telegram_id=message.from_user.id,
            telegram_bot_id=message.bot.id,
            telegram_data={
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name,
            }
        )
        await dialog_manager.start(
            states.Main.MAIN,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.SEND,
        )

    async def on_unknown_intent(self, event: ErrorEvent, dialog_manager: DialogManager):
        """Обработчик неизвестного интента"""
        logging.error("Restarting dialog: %s", event.exception)
        if event.update.callback_query:
            await event.update.callback_query.answer(
                "Bot process was restarted due to maintenance.\n"
                "Redirecting to main menu.",
            )
            if event.update.callback_query.message:
                try:
                    await event.update.callback_query.message.delete()
                except TelegramBadRequest:
                    pass
        elif event.update.message:
            await event.update.message.answer(
                "Bot process was restarted due to maintenance.\n"
                "Redirecting to main menu.",
                reply_markup=ReplyKeyboardRemove(),
            )
        actual_event = event.update.callback_query or event.update.message
        await dialog_manager.start(
            states.Main.MAIN,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.SEND,
            data={"event": actual_event},
        )

    def setup_dp(self) -> Dispatcher:
        """Настройка диспетчера"""
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        dp.message.register(self.start, F.text == "/start")
        dp.business_message.register(self.start, F.text == "/start")
        dp.errors.register(
            self.on_unknown_intent,
            ExceptionTypeFilter(UnknownIntent),
        )
        dp.include_router(self.dialog_router)
        setup_dialogs(dp)
        return dp

    async def run(self):
        """Запуск бота"""
        logging.basicConfig(level=logging.INFO)
        bot = Bot(token=os.getenv(self.token_env_name))
        dp = self.setup_dp()
        
        # Проверяем успешность обновления информации о боте
        if not await bot_repo.update_bot_info(bot):
            logging.error(f"Не удалось обновить информацию о боте {self.token_env_name}. Бот не будет запущен.")
            return
            
        await dp.start_polling(bot)
        