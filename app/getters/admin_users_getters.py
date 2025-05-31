from typing import Dict, List

from app.repo import user_repo
from app.repo.bot_token import bot_repo
from app.db.database import AsyncSessionLocal

async def get_admin_users(dialog_manager, **kwargs) -> Dict[str, List[Dict[str, str]]]:
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

        # Получаем внутренний bot_id
        bot_id = await bot_repo.get_id_by_telegram_id(telegram_bot_id, session=session)

        # Получаем только доступные тесты
        users = await user_repo.get_bot_users(bot_id=bot_id, session=session)
    
    if not users:
        return {
            "users": [],
            "no_users_text": "Нет доступных тестов для прохождения."
        }
    return {
        "users": [
            {
                "id": str(user.id), 
                "name": f"{user.name} {user.last_name if user.last_name else ''}({user.telegram_username or 'нет username'}){' - админ' if is_admin else ''}"
            } for user, is_admin in users
        ]
    }
