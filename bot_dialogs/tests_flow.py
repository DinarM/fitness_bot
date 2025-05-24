import json
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const
from sqlalchemy import select
from db import AsyncSessionLocal
from models import TestQuestion, TestType, TestUserAnswer, TestAnswer
from .states import TestsSG
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Select

async def test_type_getter(dialog_manager: DialogManager, **kwargs):
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(TestType).where(
                TestType.id == int(dialog_manager.start_data.get('test_type_id'))
            )
        )
        test_type = res.scalars().first()
        print(f"Test type: {test_type} id {int(dialog_manager.start_data.get('test_type_id'))}")
    return {
        "description": test_type.description,
        "name": test_type.name,
        "estimated_duration": test_type.estimated_duration,

    }

async def start_test(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    test_type_id = int(dialog_manager.start_data.get('test_type_id'))
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(TestQuestion).where(
                TestQuestion.test_type_id == test_type_id,
                TestQuestion.is_active == True
            ).order_by(TestQuestion.order)
        )
        questions = res.scalars().all()
        # dialog_manager.start_data.clear()
    dialog_manager.dialog_data.update({
        "question_ids": [q.id for q in questions],
        "test_user_answer": {},
        "current_index": 0,
        "question_number": 1,
    })
  
    if questions and questions[0].question_type == "text":
        await dialog_manager.switch_to(TestsSG.TEXT_TYPE_WINDOW)
    elif questions and questions[0].question_type == "single_choice":
        await dialog_manager.switch_to(TestsSG.SINGLE_CHOICE_TYPE_WINDOW)
        # return

async def text_type_getter(dialog_manager: DialogManager, **kwargs):
    async with AsyncSessionLocal() as session:
        question_text = await session.execute(
            select(TestQuestion.question_text).where(
                TestQuestion.id == dialog_manager.dialog_data["question_ids"][dialog_manager.dialog_data["current_index"]]
            )
        )
    return {
        "question_text": question_text.scalars().first(),
        "question_number": dialog_manager.dialog_data["question_number"],

    }


async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    print(type(widget))
    await message.answer(text='Вы ввели вообще не текст!')

async def on_text_received(message: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    answers = dialog_manager.dialog_data.get("test_user_answer", {})
    question_ids = dialog_manager.dialog_data.get("question_ids", [])
    print(question_ids)
    index = dialog_manager.dialog_data.get("current_index", 0)
    if question_ids and index < len(question_ids):
        question_id = question_ids[index]
        answers[question_id] = text
        dialog_manager.dialog_data["test_user_answer"] = answers
        dialog_manager.dialog_data["current_index"] += 1
        dialog_manager.dialog_data["question_number"] += 1
        print(f"Answers: {dialog_manager.dialog_data['test_user_answer']}")
        if dialog_manager.dialog_data["current_index"] < len(question_ids):
            next_question_id = dialog_manager.dialog_data["question_ids"][dialog_manager.dialog_data["current_index"]]
            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(TestQuestion.question_type).where(TestQuestion.id == next_question_id)
                )
                question_type = res.scalar()

            if question_type == "text":
                await dialog_manager.switch_to(TestsSG.TEXT_TYPE_WINDOW)
            elif question_type == "single_choice":
                await dialog_manager.switch_to(TestsSG.SINGLE_CHOICE_TYPE_WINDOW)
        else:
            # Здесь можно обработать завершение теста
            await message.answer("Тест завершен!")
            # await dialog_manager.start(TestsSG.RESULT_WINDOW)


async def single_choice_type_getter(dialog_manager: DialogManager, **kwargs):
    async with AsyncSessionLocal() as session:
        question_id = dialog_manager.dialog_data["question_ids"][dialog_manager.dialog_data["current_index"]]
        
        # Получаем вопрос
        res = await session.execute(
            select(TestQuestion).where(TestQuestion.id == question_id)
        )
        question = res.scalars().first()

        # Получаем ответы, исключая удалённые
        res_answers = await session.execute(
            select(TestAnswer)
            .where(TestAnswer.question_id == question.id)
            .order_by(TestAnswer.order)
        )
        answers = res_answers.scalars().all()

    return {
        "question_text": question.question_text,
        "possible_answers": [{"id": a.id, "name": a.text} for a in answers],
        "question_number": dialog_manager.dialog_data["question_number"],
    }

async def on_choice_handler_function(callback: CallbackQuery, select_widget, dialog_manager: DialogManager, item: dict):
    answers = dialog_manager.dialog_data.get("test_user_answer", {})
    question_ids = dialog_manager.dialog_data.get("question_ids", [])
    index = dialog_manager.dialog_data.get("current_index", 0)
    
    if question_ids and index < len(question_ids):
        question_id = question_ids[index]
        answers[question_id] = item["name"]
        dialog_manager.dialog_data["test_user_answer"] = answers
        dialog_manager.dialog_data["current_index"] += 1
        dialog_manager.dialog_data["question_number"] += 1
        print(f"Answers: {dialog_manager.dialog_data['test_user_answer']}")
        
        if dialog_manager.dialog_data["current_index"] < len(question_ids):
            next_question_id = dialog_manager.dialog_data["question_ids"][dialog_manager.dialog_data["current_index"]]
            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(TestQuestion.question_type).where(TestQuestion.id == next_question_id)
                )
                question_type = res.scalar()

            if question_type == "text":
                await dialog_manager.switch_to(TestsSG.TEXT_TYPE_WINDOW)
            elif question_type == "single_choice":
                await dialog_manager.switch_to(TestsSG.SINGLE_CHOICE_TYPE_WINDOW)
        else:
            # Здесь можно обработать завершение теста
            await callback.message.answer("Тест завершен!")
            # await dialog_manager.start(TestsSG.RESULT_WINDOW)

question_window = Window(
        Format('<b>{name}!</b>\n'),
        Format('<b>{description}!</b>\n'),
        Format('<b>Займет времени: {estimated_duration}!</b>\n', when=lambda data, *_: data.get('estimated_duration') is not None),
        Button(Const('Начать тестирование ▶️'), id='b_next', on_click=start_test),
        getter=test_type_getter,
        state=TestsSG.START_WINDOW,
        parse_mode="HTML",
    )
text_type_dialog = Window(
        Format('{question_number}. {question_text}'),
        # Button(Const('Кнопка'), id='button_start', on_click=go_start),
        TextInput(
            id='text_input',
            on_success=on_text_received
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        getter=text_type_getter,
        state=TestsSG.TEXT_TYPE_WINDOW,
    )
single_choice_type_dialog = Window(
        Format('{question_number}. {question_text}'),
        Select(
            Format("🔹 {item[name]}"),
            id="answer_select",
            item_id_getter=lambda item: item["id"],
            items="possible_answers",
            on_click=on_choice_handler_function,
        ),
        getter=single_choice_type_getter,
        state=TestsSG.SINGLE_CHOICE_TYPE_WINDOW,
        )


tests_dialog = Dialog(
    question_window,
    text_type_dialog,
    single_choice_type_dialog,
)