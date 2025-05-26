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