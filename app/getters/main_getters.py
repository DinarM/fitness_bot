from typing import Dict

from app.repo import user_repo
from app.repo.bot_token import bot_repo
from app.db.database import AsyncSessionLocal

async def main_getter(dialog_manager, **kwargs) -> Dict[str, bool]:
    """
    Получает и форматирует список тестов бота для использования в диалоге
    Args:
        dialog_manager: Менеджер диалога
        **kwargs: Дополнительные параметры
    Returns:
        Dict[str, List[Dict[str, str]]]: Словарь с тестами в формате для диалога
    """
    # Получаем bot_id и user_id
    telegram_bot_id = dialog_manager.event.bot.id

    async with AsyncSessionLocal() as session:
        user = await user_repo.get_user_by_telegram_id(telegram_id=dialog_manager.event.from_user.id, session=session)

        # Получаем внутренний bot_id
        bot_id = await bot_repo.get_id_by_telegram_id(telegram_bot_id, session=session)

        is_admin = await user_repo.check_user_is_admin(
            user_id=user.id,
            bot_id=bot_id,
            session=session
        )

    return {"is_admin": is_admin}

def admin_flag_visible(data, widget, manager) -> bool:
    """
    Проверяет, является ли пользователь администратором
    Args:
        data: Данные виджета
        widget: Виджет
        manager: Менеджер диалога
    Returns:
        bool: True если пользователь администратор, иначе False
    """
    return data.get("is_admin", False)