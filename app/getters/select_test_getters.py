from typing import Dict, List
from app.repo import test_types_repo, user_repo
from app.repo.bot_token import bot_repo

async def get_test_types_for_dialog(dialog_manager, **kwargs) -> Dict[str, List[Dict[str, str]]]:
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
    user = await user_repo.get_user_by_telegram_id(telegram_id=dialog_manager.event.from_user.id)

    # Получаем внутренний bot_id
    bot_id = await bot_repo.get_id_by_telegram_id(telegram_bot_id)

    # Получаем только доступные тесты
    test_types = await test_types_repo.get_available_for_user(
        bot_id=bot_id,
        user_id=user.id,
        only_active=True
    )
    
    if not test_types:
        return {
            "test_types": [],
            "no_tests_text": "Нет доступных тестов для прохождения."
        }
    return {
        "test_types": [
            {"id": str(tt.id), "name": tt.name} for tt in test_types
        ]
    }