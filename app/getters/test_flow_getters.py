from aiogram_dialog import DialogManager
from app.repo import test_types_repo, test_question_repo, test_answer_repo



async def start_test_getter(dialog_manager: DialogManager, **kwargs):
    test_type_id = int(dialog_manager.start_data.get('test_type_id'))
    test_type = await test_types_repo.get_by_id(test_type_id=test_type_id)
        
    return {
        "description": test_type.description,
        "name": test_type.name,
        "estimated_duration": test_type.estimated_duration,
    }

async def question_input_getter(dialog_manager: DialogManager, **kwargs):
    question_id = dialog_manager.dialog_data["question_ids"][dialog_manager.dialog_data["current_index"]]
    question = await test_question_repo.get_by_id(id=question_id)
    return {
        "question_text": question.question_text,
        "question_number": dialog_manager.dialog_data["question_number"],
    }

async def single_choice_type_getter(dialog_manager: DialogManager, **kwargs):
    question_id = dialog_manager.dialog_data["question_ids"][dialog_manager.dialog_data["current_index"]]
    
    # Получаем вопрос
    question = await test_question_repo.get_by_id(id=question_id)

    # Получаем ответы, исключая удалённые
    answers = await test_answer_repo.get_multi_by_test_question(question_id=question.id)

    return {
        "question_text": question.question_text,
        "possible_answers": [{"id": a.id, "name": a.text} for a in answers],
        "question_number": dialog_manager.dialog_data["question_number"],
    }

async def final_review_getter(dialog_manager: DialogManager, **kwargs):
    """Геттер для финального просмотра ответов"""
    question_ids = dialog_manager.dialog_data.get('question_ids', [])
    user_answers = dialog_manager.dialog_data.get('test_user_answer', {})
    
    review_data = []
    for i, question_id in enumerate(question_ids, 1):
        question = await test_question_repo.get_by_id(id=question_id)
        if not question:
            continue
            
        user_answer = user_answers.get(question_id)
        answers = await test_answer_repo.get_multi_by_test_question(question_id=question_id)
        
        # Форматируем ответ в зависимости от типа вопроса
        if question.question_type in ['multiple_choice', 'single_choice']:
            if not user_answer:
                answer_text = 'Нет ответа'
            else:
                # Преобразуем ID ответов в текст
                answer_ids = user_answer if isinstance(user_answer, list) else [user_answer]
                answer_texts = []
                for answer_id in answer_ids:
                    answer = next((a for a in answers if str(a.id) == str(answer_id)), None)
                    if answer:
                        answer_texts.append(answer.text)
                answer_text = ', '.join(answer_texts) if answer_texts else 'Нет ответа'
        else:
            answer_text = str(user_answer) if user_answer else 'Нет ответа'
        
        review_data.append({
            'question_number': i,
            'question': question.question_text,
            'answer': answer_text
        })
    
    # Преобразуем список в строку с форматированием
    formatted_text = ''
    for item in review_data:
        formatted_text += f'<b>Вопрос {item["question_number"]}:</b>\n{item["question"]}\n<i>Ваш ответ:</i> {item["answer"]}\n\n'
    
    return {
        'formatted_text': formatted_text
    }