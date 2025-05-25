from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from app.dialogs.states import TestsSG
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select
from app.repo import test_question_repo



async def start_test(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    test_type_id = int(dialog_manager.start_data.get('test_type_id'))
    
    questions = await test_question_repo.get_multi_by_test_type(test_type_id=test_type_id)
    
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


async def no_text(message: Message):
    await message.answer(text='Вы ввели вообще не текст!')

async def answer_handler(
    event: Message | CallbackQuery,
    widget: TextInput | Select,
    dialog_manager: DialogManager,
    answer: str | int
) -> None:
    """
    Универсальный обработчик ответов для разных типов вопросов
    Args:
        event: Объект сообщения или callback
        widget: Виджет ввода (TextInput или Select)
        dialog_manager: Менеджер диалога
        answer: Значение ответа (текст или ID)
    """
    dialog_data = dialog_manager.dialog_data
    current_index = dialog_data.get('current_index', 0)
    question_ids = dialog_data.get('question_ids', [])
    
    # Проверяем валидность индекса
    if not question_ids or current_index >= len(question_ids):
        await event.answer('Ошибка: вопрос не найден')
        return
        
    # Сохраняем ответ
    question_id = question_ids[current_index]
    answers = dialog_data.get('test_user_answer', {})
    answers[question_id] = answer
    dialog_data['test_user_answer'] = answers
    
    # Увеличиваем счетчики
    dialog_data['current_index'] = current_index + 1
    dialog_data['question_number'] = dialog_data.get('question_number', 1) + 1
    
    # Проверяем, есть ли следующий вопрос
    if current_index + 1 >= len(question_ids):
        await event.answer('Тест завершен!')
        return
        
    # Получаем следующий вопрос
    next_question = await test_question_repo.get_by_id(id=question_ids[current_index + 1])
    if not next_question:
        await event.answer('Ошибка: следующий вопрос не найден')
        return
        
    # Переключаемся на соответствующее окно
    window_map = {
        'text': TestsSG.TEXT_TYPE_WINDOW,
        'single_choice': TestsSG.SINGLE_CHOICE_TYPE_WINDOW
    }
    
    next_window = window_map.get(next_question.question_type)
    if next_window:
        await dialog_manager.switch_to(next_window)
    else:
        await event.answer(f'Ошибка: неизвестный тип вопроса {next_question.question_type}')