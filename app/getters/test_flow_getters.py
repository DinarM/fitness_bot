import json
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import TestQuestion, TestType, TestUserAnswer, TestAnswer
from app.dialogs.states import TestsSG
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Select
from app.repo import test_types_repo


async def start_test_getter(dialog_manager: DialogManager, **kwargs):
    test_type_id = int(dialog_manager.start_data.get('test_type_id'))
    test_type = await test_types_repo.get_by_id(test_type_id=test_type_id)
        
    return {
        "description": test_type.description,
        "name": test_type.name,
        "estimated_duration": test_type.estimated_duration,
    }