import json
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import TestQuestion, TestType, TestUserAnswer, TestAnswer
from app.getters.test_flow_getters import start_test_getter
from app.dialogs.states import TestsSG
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Select
from app.repo import test_question_repo



async def start_test(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    test_type_id = int(dialog_manager.start_data.get('test_type_id'))
    
    questions = await test_question_repo.get_by_test_type(test_type_id=test_type_id)
    
    if not questions:
        await callback.answer('В этом тесте нет активных вопросов', show_alert=True)
        return
        
    dialog_manager.start_data.clear()
    
    dialog_manager.dialog_data.update({
        "question_ids": [q.id for q in questions],
        "test_user_answer": {},
        "current_index": 0,
        "question_number": 1,
    })
  
    if questions[0].question_type == "text":
        await dialog_manager.switch_to(TestsSG.TEXT_TYPE_WINDOW)
    elif questions[0].question_type == "single_choice":
        await dialog_manager.switch_to(TestsSG.SINGLE_CHOICE_TYPE_WINDOW)
        # return