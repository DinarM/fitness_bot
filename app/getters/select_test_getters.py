from typing import Dict, List
from app.repo.test_types import test_types_repo

async def get_test_types_for_dialog(dialog_manager, **kwargs) -> Dict[str, List[Dict[str, str]]]:
    """
    Получает и форматирует список тестов бота для использования в диалоге
    Args:
        dialog_manager: Менеджер диалога
        **kwargs: Дополнительные параметры
    Returns:
        Dict[str, List[Dict[str, str]]]: Словарь с тестами в формате для диалога
    """
    test_types = await test_types_repo.get_by_telegram_bot(
        telegram_bot_id=dialog_manager.event.bot.id
    )
    
    return {
        "test_types": [
            {"id": str(tt.id), "name": tt.name} for tt in test_types
        ]
    }