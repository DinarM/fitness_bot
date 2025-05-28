import json
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from app.dialogs.states import TestsSG
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.kbd import Multiselect
from app.repo import test_question_repo, bot_repo, user_repo, test_user_answer_repo, test_answer_repo
from typing import Any, List, Union
from aiogram import Bot
from aiogram_dialog.widgets.input import ManagedTextInput
from app.db.database import AsyncSessionLocal

async def get_next_window(question_type: str) -> TestsSG:
    """Получает следующее окно на основе типа вопроса"""
    window_map = {
        'text': TestsSG.TEXT_TYPE_WINDOW,
        'single_choice': TestsSG.SINGLE_CHOICE_TYPE_WINDOW,
        'multiple_choice': TestsSG.MULTIPLE_CHOICE_TYPE_WINDOW,
        'numeric': TestsSG.NUMERIC_TYPE_WINDOW,
        'rating': TestsSG.RATING_TYPE_WINDOW,
    }
    return window_map.get(question_type)

async def save_answer(
    dialog_manager: DialogManager,
    question_id: int,
    answer: Union[str, List[str]]
) -> None:
    """Сохраняет ответ пользователя"""
    answers = dialog_manager.dialog_data.get('test_user_answer', {})
    answers[question_id] = answer
    dialog_manager.dialog_data['test_user_answer'] = answers

async def get_current_question_data(dialog_manager: DialogManager) -> tuple[int, List[int], int]:
    """Получает данные текущего вопроса"""
    dialog_data = dialog_manager.dialog_data
    current_index = dialog_data.get('current_index', 0)
    question_ids = dialog_data.get('question_ids', [])
    question_id = question_ids[current_index] if question_ids else None
    return current_index, question_ids, question_id

async def start_test(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    test_type_id = dialog_manager.start_data.get('test_type_id')
    if test_type_id is None:
        test_type_id = dialog_manager.dialog_data.get('test_type_id')
    
    if test_type_id is None:
        await callback.answer('Ошибка: не удалось определить тип теста', show_alert=True)
        return
        
    test_type_id = int(test_type_id)
    questions = await test_question_repo.get_multi_by_test_type(test_type_id=test_type_id)
    
    if not questions:
        await callback.answer('В этом тесте нет активных вопросов', show_alert=True)
        return
        
    dialog_manager.dialog_data.update({
        "test_type_id": test_type_id,
        "question_ids": [q.id for q in questions],
        "current_index": 0,
        "question_number": 1,
    })
  
    next_window = await get_next_window(questions[0].question_type)
    if next_window:
        await dialog_manager.switch_to(next_window)

async def next_question(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    current_index, question_ids, _ = await get_current_question_data(dialog_manager)
    
    # Увеличиваем счетчики
    dialog_manager.dialog_data['current_index'] = current_index + 1
    dialog_manager.dialog_data['question_number'] = dialog_manager.dialog_data.get('question_number', 1) + 1
    
    if current_index + 1 >= len(question_ids):
        # Если это был последний вопрос, переходим к финальному окну
        await dialog_manager.switch_to(TestsSG.FINAL_REVIEW_WINDOW)
        return
        
    next_question = await test_question_repo.get_by_id(id=question_ids[current_index + 1])
    if not next_question:
        await callback.answer('Ошибка: следующий вопрос не найден')
        return
        
    next_window = await get_next_window(next_question.question_type)
    if next_window:
        await dialog_manager.switch_to(next_window)
    else:
        await callback.answer(f'Ошибка: неизвестный тип вопроса {next_question.question_type}')

async def no_text(message: Message):
    await message.answer(text='Вы ввели вообще не текст!')

async def single_answer_handler(
    callback: CallbackQuery | Message, 
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str | None = None 
) -> None:
    is_text_input = isinstance(callback, Message)
    answer = callback.text if is_text_input else item_id
    
    current_index, question_ids, question_id = await get_current_question_data(dialog_manager)
    
    if not question_ids or current_index >= len(question_ids):
        await callback.answer('Ошибка: вопрос не найден')
        return
        
    await save_answer(dialog_manager, question_id, answer)
    
    if is_text_input:
        # Удаляем сообщение пользователя
        try:
            await callback.delete()
        except Exception:
            pass
        bot: Bot = dialog_manager.event.bot  # получаем экземпляр бота
        chat_id = dialog_manager.event.chat.id
        message_id = dialog_manager.current_stack().last_message_id
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception:
            pass
        
        await next_question(callback, None, dialog_manager)

async def multi_answer_handler(
    callback: CallbackQuery,
    widget: Multiselect,
    dialog_manager: DialogManager,
    item_id: str,
):
    current_index, question_ids, question_id = await get_current_question_data(dialog_manager)
    
    if not question_ids or current_index >= len(question_ids):
        await callback.answer('Ошибка: вопрос не найден')
        return
        
    answers = dialog_manager.dialog_data.get('test_user_answer', {})
    selected = answers.get(question_id, [])
    
    if item_id in selected:
        selected.remove(item_id)
    else:
        selected.append(item_id)
        
    await save_answer(dialog_manager, question_id, selected)
    await callback.answer()

def has_selected_items(data: Any, widget: Any, manager: DialogManager) -> bool: 
    """Проверяет, есть ли выбранные ответы для текущего вопроса"""
    dialog_data = manager.dialog_data
    current_index = dialog_data.get('current_index', 0)
    question_ids = dialog_data.get('question_ids', [])
    
    if not question_ids or current_index >= len(question_ids):
        return False
        
    question_id = question_ids[current_index]
    answers = dialog_data.get('test_user_answer', {})
    
    # Проверяем, есть ли ответ для текущего вопроса
    return bool(answers.get(question_id))

def check_numeric_type(text: str) -> None:
    """Проверяет, является ли введенное значение числом"""
    try:
        float(text)
    except ValueError:
        raise ValueError()

async def error_numeric_type(
    message: Message,
    widget: ManagedTextInput, 
    dialog_manager: DialogManager,
    error: ValueError
) -> None:
    """Обработка ошибки при вводе некорректного значения для числового типа"""
    await message.answer('Введенное значение не является числом. \nПримеры допустимых значений: 42, 3.14, -5, 0.001')

async def save_test_results(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Сохраняет результаты теста в БД"""
    test_type_id = int(dialog_manager.dialog_data.get('test_type_id'))
    answers = dialog_manager.dialog_data.get('test_user_answer', {})
    
    # Преобразуем ID в тексты
    formatted_answers = {}
    for question_id, answer in answers.items():
        question = await test_question_repo.get_by_id(id=int(question_id))
        if not question:
            continue
            
        question_text = question.question_text
        if question.question_type in ['multiple_choice', 'single_choice']:
            answers_list = await test_answer_repo.get_multi_by_test_question(question_id=int(question_id))
            answer_ids = answer if isinstance(answer, list) else [answer]
            answer_texts = []
            for answer_id in answer_ids:
                answer_obj = next((a for a in answers_list if str(a.id) == str(answer_id)), None)
                if answer_obj:
                    answer_texts.append(answer_obj.text)
            formatted_answers[question_text] = answer_texts if answer_texts else 'Нет ответа'
        else:
            formatted_answers[question_text] = answer if answer else 'Нет ответа'
    
    answers_json = json.dumps(formatted_answers, ensure_ascii=False)
    
    async with AsyncSessionLocal() as session:
        bot_id = await bot_repo.get_id_by_telegram_id(telegram_bot_id=dialog_manager.event.bot.id, session=session)
        user_id = await user_repo.get_user_by_telegram_id(telegram_id=callback.from_user.id, session=session)

        print(f'user_id: {user_id}, bot_id: {bot_id}, test_type_id: {test_type_id}, answers: {answers_json}')

        try:
            await test_user_answer_repo.create_test_result(
                test_type_id=test_type_id,
                user_id=user_id.id,
                bot_id=bot_id,
                answers=answers_json,
                session=session
            )
        except Exception as e:
            await callback.answer(f'Ошибка при сохранении результатов теста: {str(e)}', show_alert=True)
            return
    
    await callback.answer('Результаты теста успешно сохранены!')
    await dialog_manager.done()
