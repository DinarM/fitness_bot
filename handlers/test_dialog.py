# from aiogram_dialog import Dialog, Window, DialogManager
# from aiogram_dialog.widgets.text import Const, Format
# from aiogram_dialog.widgets.kbd import Button, Select, Group, Start
# from aiogram_dialog.widgets.input import TextInput
# from aiogram import Dispatcher, types
# from aiogram.types import CallbackQuery, Message
# from aiogram.filters import Command
# from aiogram import Router, F
# from aiogram.fsm.state import State, StatesGroup
# from sqlalchemy import select, and_
# from models import User, TestType, TestQuestion, TestUserAnswer, BotToken, user_bots
# from db import AsyncSessionLocal
# import json

# # Создаем роутер для диалога
# router = Router()

# # Состояния диалога
# class TestDialog(StatesGroup):
#     MAIN = State()
#     QUESTION = State()
#     FINISH = State()

# # Ключи для данных диалога
# class TestData:
#     QUESTIONS = "questions"
#     CURRENT_INDEX = "current_index"
#     USER_ID = "user_id"
#     BOT_ID = "bot_id"
#     TEST_TYPE_ID = "test_type_id"
#     TEST_USER_ANSWER_ID = "test_user_answer_id"
#     SELECTED_OPTIONS = "selected_options"

# async def get_test_data(dialog_manager: DialogManager, **kwargs):
#     """Получение данных для отображения теста"""
#     data = dialog_manager.dialog_data
#     current_index = data.get(TestData.CURRENT_INDEX, 0)
#     questions = data.get(TestData.QUESTIONS, [])
    
#     if current_index >= len(questions):
#         return {
#             "status": "finished",
#             "question": None,
#             "options": [],
#             "current_index": current_index + 1,
#             "total_questions": len(questions)
#         }
    
#     async with AsyncSessionLocal() as session:
#         question = await session.get(TestQuestion, questions[current_index])
#         if not question:
#             # Если вопрос не найден, переходим к следующему
#             current_index += 1
#             await dialog_manager.update_data({TestData.CURRENT_INDEX: current_index})
#             if current_index >= len(questions):
#                 return {
#                     "status": "finished",
#                     "question": None,
#                     "options": [],
#                     "current_index": current_index + 1,
#                     "total_questions": len(questions)
#                 }
#             # Рекурсивно получаем следующий вопрос
#             return await get_test_data(dialog_manager, **kwargs)
            
#         options = []
#         if question.question_type in ["single_choice", "multiple_choice", "rating"]:
#             if question.question_type == "rating":
#                 options = list(map(str, range(1, 11)))
#             elif question.possible_answers:
#                 try:
#                     options = json.loads(question.possible_answers)
#                 except json.JSONDecodeError:
#                     options = []
    
#     return {
#         "status": "in_progress",
#         "question": question,
#         "options": options,
#         "current_index": current_index + 1,
#         "total_questions": len(questions)
#     }

# async def get_test_questions(session, test_type_id: int, bot_id: int):
#     """Получение списка вопросов для теста"""
#     questions_stmt = select(TestQuestion).where(
#         TestQuestion.test_type_id == test_type_id,
#         TestQuestion.is_active == True,
#         TestQuestion.bot_id == bot_id
#     ).order_by(TestQuestion.id)
#     result = await session.execute(questions_stmt)
#     return result.scalars().all()

# async def create_test_user_answer(session, user_id: int, test_type_id: int, bot_id: int):
#     """Создание записи для ответов пользователя"""
#     test_user_answer = TestUserAnswer(
#         user_id=user_id,
#         test_type_id=test_type_id,
#         answer=json.dumps({}),
#         bot_id=bot_id
#     )
#     session.add(test_user_answer)
#     await session.commit()
#     return test_user_answer

# async def save_answer(dialog_manager: DialogManager, answer):
#     """Сохранение ответа пользователя"""
#     data = dialog_manager.dialog_data
#     current_index = data.get(TestData.CURRENT_INDEX, 0)
#     questions = data.get(TestData.QUESTIONS, [])
#     test_user_answer_id = data.get(TestData.TEST_USER_ANSWER_ID)
    
#     if current_index >= len(questions):
#         return
    
#     question_id = questions[current_index]
    
#     async with AsyncSessionLocal() as session:
#         test_user_answer = await session.get(TestUserAnswer, test_user_answer_id)
#         answers_dict = json.loads(test_user_answer.answer)
#         answers_dict[str(question_id)] = answer
#         test_user_answer.answer = json.dumps(answers_dict, ensure_ascii=False)
#         await session.commit()

# async def process_answer(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
#     """Обработка ответа с выбором варианта"""
#     await save_answer(dialog_manager, item_id)
#     await process_next_question(dialog_manager)

# async def process_text_answer(message: types.Message, widget, dialog_manager: DialogManager, text: str):
#     """Обработка текстового ответа"""
#     await save_answer(dialog_manager, text)
#     await process_next_question(dialog_manager)

# async def process_next_question(dialog_manager: DialogManager):
#     """Переход к следующему вопросу или завершение теста"""
#     data = dialog_manager.dialog_data
#     current_index = data.get(TestData.CURRENT_INDEX, 0)
#     questions = data.get(TestData.QUESTIONS, [])
    
#     current_index += 1
#     await dialog_manager.update_data({TestData.CURRENT_INDEX: current_index})
    
#     if current_index >= len(questions):
#         await dialog_manager.switch_to(TestDialog.FINISH)
#     else:
#         await dialog_manager.switch_to(TestDialog.QUESTION)

# async def process_multiple_choice(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
#     """Обработка выбора нескольких вариантов"""
#     data = dialog_manager.dialog_data
#     selected_options = data.get(TestData.SELECTED_OPTIONS, [])
    
#     if item_id in selected_options:
#         selected_options.remove(item_id)
#     else:
#         selected_options.append(item_id)
    
#     await dialog_manager.update_data({TestData.SELECTED_OPTIONS: selected_options})
#     await callback.answer()

# async def process_multiple_done(callback: CallbackQuery, widget, dialog_manager: DialogManager):
#     """Завершение выбора нескольких вариантов"""
#     data = dialog_manager.dialog_data
#     selected_options = data.get(TestData.SELECTED_OPTIONS, [])
#     await save_answer(dialog_manager, selected_options)
#     await process_next_question(dialog_manager)

# async def process_int_answer(message: Message, widget, dialog_manager: DialogManager, text: str):
#     """Обработка числового ответа"""
#     try:
#         answer = int(text)
#         await save_answer(dialog_manager, answer)
#         await process_next_question(dialog_manager)
#     except ValueError:
#         await message.answer("Пожалуйста, введите целое число")

# # Обновляем окно с вопросом, добавляя поддержку multiple_choice
# question_window = Window(
#     Format("Вопрос {current_index} из {total_questions}:\n{question.question_text if question else 'Вопрос не найден'}"),
#     Group(
#         Select(
#             Format("{item}"),
#             id="answer_select",
#             items="options",
#             item_id_getter=lambda x: x,
#             on_click=process_answer
#         ),
#         when=lambda data: data["question"] and data["question"].question_type in ["single_choice", "rating"]
#     ),
#     Group(
#         Select(
#             Format("✅ {item}" if "{item}" in "selected_options" else "{item}"),
#             id="multiple_select",
#             items="options",
#             item_id_getter=lambda x: x,
#             on_click=process_multiple_choice
#         ),
#         Button(
#             Const("Готово"),
#             id="multiple_done",
#             on_click=process_multiple_done
#         ),
#         when=lambda data: data["question"] and data["question"].question_type == "multiple_choice"
#     ),
#     Group(
#         TextInput(
#             id="text_answer",
#             on_success=process_text_answer
#         ),
#         when=lambda data: data["question"] and data["question"].question_type == "text"
#     ),
#     Group(
#         TextInput(
#             id="int_answer",
#             on_success=process_int_answer
#         ),
#         when=lambda data: data["question"] and data["question"].question_type == "int"
#     ),
#     state=TestDialog.QUESTION,
#     getter=get_test_data
# )

# # Окно завершения
# finish_window = Window(
#     Const("Тест завершен!"),
#     state=TestDialog.FINISH
# )

# # Создаем диалог
# test_dialog = Dialog(
#     question_window,
#     finish_window
# )

# # Регистрируем диалог
# def register_dialogs(dp: Dispatcher):
#     dp.include_router(test_dialog)

# # Хендлер для начала теста
# @router.message(Command("start_test"))
# async def cmd_start_test(message: Message, dialog_manager: DialogManager):
#     """Начало теста с использованием диалога"""
#     async with AsyncSessionLocal() as session:
#         # Определяем bot_id по токену
#         bot_token = (await session.execute(select(BotToken).where(BotToken.token == message.bot.token))).scalar_one_or_none()
#         if not bot_token:
#             await message.answer("Бот не найден в системе.")
#             return
#         bot_id = bot_token.id

#         # Получаем/создаём пользователя
#         user = await get_or_create_user(session, message.from_user.username, bot_id)

#         # Выбираем тип теста
#         test_type_obj = (await session.execute(select(TestType).where(TestType.bot_id == bot_id))).scalars().first()
#         if not test_type_obj:
#             await message.answer("Тип теста не найден для этого бота.")
#             return

#         # Получаем вопросы
#         questions = await get_test_questions(session, test_type_obj.id, bot_id)
#         if not questions:
#             await message.answer("Нет активных вопросов для теста.")
#             return

#         # Создаем запись для ответов
#         test_user_answer = await create_test_user_answer(session, user.id, test_type_obj.id, bot_id)

#         # Инициализируем данные диалога
#         dialog_data = {
#             TestData.QUESTIONS: [q.id for q in questions],
#             TestData.CURRENT_INDEX: 0,
#             TestData.USER_ID: user.id,
#             TestData.BOT_ID: bot_id,
#             TestData.TEST_TYPE_ID: test_type_obj.id,
#             TestData.TEST_USER_ANSWER_ID: test_user_answer.id,
#             TestData.SELECTED_OPTIONS: []
#         }

#         # Запускаем диалог
#         await dialog_manager.start(
#             TestDialog.QUESTION,
#             data=dialog_data
#         )

# async def get_or_create_user(session, telegram_username: str, bot_id: int) -> User:
#     """Получение или создание пользователя"""
#     stmt = select(User).where(User.telegram_username == telegram_username)
#     result = await session.execute(stmt)
#     user = result.scalar_one_or_none()
#     if not user:
#         user = User(telegram_username=telegram_username)
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)
    
#     # Проверяем связь user-bot
#     link_stmt = select(user_bots).where(user_bots.c.user_id == user.id, user_bots.c.bot_id == bot_id)
#     link = (await session.execute(link_stmt)).first()
#     if not link:
#         await session.execute(user_bots.insert().values(user_id=user.id, bot_id=bot_id))
#         await session.commit()
#     return user 