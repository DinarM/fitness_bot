# from aiogram import Router, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.filters import Command
# from sqlalchemy import select, and_
# from models import User, TestType, TestQuestion, TestUserAnswer, BotToken, user_bots
# from db import AsyncSessionLocal
# import json
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.exceptions import TelegramBadRequest

# router = Router()

# class TestStates(StatesGroup):
#     waiting_for_questions = State()
#     waiting_for_answer = State()

# @router.message(Command("start_test"))
# async def cmd_start_test(message: types.Message, state: FSMContext):
#     """
#     Начало теста: найдём или создадим юзера, загрузим вопросы и начнём опрос.
#     """
#     async with AsyncSessionLocal() as session:
#         # 1. Определяем bot_id по токену
#         bot_token = (await session.execute(select(BotToken).where(BotToken.token == message.bot.token))).scalar_one_or_none()
#         if not bot_token:
#             await message.answer("Бот не найден в системе.")
#             return
#         bot_id = bot_token.id

#         # 2. Получаем/создаём пользователя и связь с ботом
#         user = await get_or_create_user(session, message.from_user.username, bot_id)

#         # 3. Выбираем тип теста (демо-пример: первый доступный для этого бота)
#         test_type_obj = (await session.execute(select(TestType).where(TestType.bot_id == bot_id))).scalars().first()
#         if not test_type_obj:
#             await message.answer("Тип теста не найден для этого бота.")
#             return
#         test_type_id = test_type_obj.id

#         # Получаем вопросы
#         questions_stmt = select(TestQuestion).where(
#             TestQuestion.test_type_id == test_type_id,
#             TestQuestion.is_active == True,
#             TestQuestion.bot_id == bot_id
#         ).order_by(TestQuestion.id)
#         result = await session.execute(questions_stmt)
#         questions = result.scalars().all()

#         if not questions:
#             await message.answer("Нет активных вопросов для теста.")
#             return

#         result = await session.execute(
#             select(TestUserAnswer).where(
#                 and_(
#                     TestUserAnswer.user_id == user.id,
#                     TestUserAnswer.test_type_id == test_type_id,
#                     TestUserAnswer.bot_id == bot_id
#                 )
#             )
#         )
#         existing_answer = result.scalars().first()
#         if existing_answer and not test_type_obj.allow_multiple_passes:
#             await message.answer("Вы уже проходили этот тест. Повторное прохождение запрещено.")
#             return
#         test_user_answer = TestUserAnswer(
#             user_id=user.id,
#             test_type_id=test_type_id,
#             answer=json.dumps({}),
#             bot_id=bot_id
#         )
#         session.add(test_user_answer)
#         await session.commit()
#         test_user_answer_id = test_user_answer.id

#         await state.update_data(
#             questions=[q.id for q in questions],
#             current_index=0,
#             user_id=user.id,
#             bot_id=bot_id,
#             test_type_id=test_type_id,
#             test_user_answer_id=test_user_answer_id
#         )

#         await message.answer("Начинаем тест!")
#         await ask_next_question(message, state)

# async def ask_next_question(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     questions = data["questions"]
#     current_index = data["current_index"]
#     bot_id = data["bot_id"]

#     if current_index >= len(questions):
#         await message.answer("Тест завершён!")
#         await state.clear()
#         return

#     question_id = questions[current_index]
#     async with AsyncSessionLocal() as session:
#         question_obj = await session.get(TestQuestion, question_id)
#         if not question_obj or question_obj.bot_id != bot_id:
#             await message.answer("Вопрос не найден или не принадлежит этому боту.")
#             await state.clear()
#             return

#     q_type = question_obj.question_type
#     question_text = f"Вопрос {current_index+1}: {question_obj.question_text}"
    
#     # Будем собирать клавиатуру (если нужна)
#     keyboard = None

#     # 1. TEXT-вопрос (свободный ввод)
#     if q_type == "text":
#         # Просто выводим текст. Ответ ловим в process_answer
#         await message.answer(question_text)
#         await state.set_state(TestStates.waiting_for_answer)
#         return

#     # 2. SINGLE CHOICE (один вариант) или RATING (шкала)
#     elif q_type in ["single_choice", "rating"]:
#         answers_list = []
#         if q_type == "rating":
#             answers_list = list(map(str, range(1, 11)))
#         elif question_obj.possible_answers:
#             try:
#                 answers_list = json.loads(question_obj.possible_answers)
#             except json.JSONDecodeError:
#                 pass

#         if answers_list:
#             buttons = []
#             for ans in answers_list:
#                 buttons.append([InlineKeyboardButton(text=str(ans), callback_data=f"ans:{ans}")])
#             keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

#         await message.answer(question_text, reply_markup=keyboard)
#         await state.set_state(TestStates.waiting_for_answer)
#         return

#     # 3. MULTIPLE CHOICE (несколько вариантов)
#     elif q_type == "multiple_choice":
#         # Упрощённый вариант: даём несколько кнопок,
#         # а последней кнопкой «Готово» — подтверждаем.
#         answers_list = []
#         if question_obj.possible_answers:
#             try:
#                 answers_list = json.loads(question_obj.possible_answers)
#             except json.JSONDecodeError:
#                 pass

#         # Допустим, мы сохраняем в FSM выбранные варианты
#         await state.update_data(selected_options=[])

#         if answers_list:
#             # Генерируем Inline-кнопки, где при нажатии на вариант вызываем callback с «mul:...»
#             buttons = []
#             for ans in answers_list:
#                 buttons.append([InlineKeyboardButton(text=ans, callback_data=f"mul:{ans}")])
#             # Кнопка «Готово»
#             buttons.append([InlineKeyboardButton(text="Готово", callback_data=f"mul_done")])
#             keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

#         await message.answer(question_text, reply_markup=keyboard)
#         await state.set_state(TestStates.waiting_for_answer)
#         return
#     # 5. INT (только цифры)
#     elif q_type == "int":
#         # Попросим ввести число, проверим потом при получении ответа.
#         hint = question_text + "\n(Введите целое число)"
#         await message.answer(hint)
#         await state.set_state(TestStates.waiting_for_answer)
#         return

#     else:
#         # Если тип неизвестен, считаем его текстовым
#         await message.answer(question_text)
#         await state.set_state(TestStates.waiting_for_answer)

# @router.message(TestStates.waiting_for_answer, F.text)
# async def process_answer(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     questions = data["questions"]
#     current_index = data["current_index"]
#     user_id = data["user_id"]
#     bot_id = data["bot_id"]
#     test_type_id = data["test_type_id"]
#     test_user_answer_id = data["test_user_answer_id"]

#     question_id = questions[current_index]
#     user_answer = message.text

#     # Сохраняем ответ в JSON в одной записи TestUserAnswer
#     async with AsyncSessionLocal() as session:
#         test_user_answer = await session.get(TestUserAnswer, test_user_answer_id)
#         answers_dict = json.loads(test_user_answer.answer)
#         answers_dict[str(question_id)] = user_answer
#         test_user_answer.answer = json.dumps(answers_dict, ensure_ascii=False)
#         await session.commit()

#     # Переходим к следующему
#     current_index += 1
#     await state.update_data(current_index=current_index)
#     await ask_next_question(message, state)

# # Доп. функция get_or_create_user с поддержкой SaaS
# async def get_or_create_user(session, telegram_username: str, bot_id: int) -> User:
#     from models import user_bots
#     stmt = select(User).where(User.telegram_username == telegram_username)
#     result = await session.execute(stmt)
#     user = result.scalar_one_or_none()
#     if not user:
#         # Создаём нового
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


# @router.callback_query(F.data.startswith("ans:"))
# async def process_inline_answer(callback: types.CallbackQuery, state: FSMContext):
#     """
#     Обрабатываем ответ пользователя, когда он нажал на кнопку варианта.
#     """
#     data = await state.get_data()
#     questions = data["questions"]
#     current_index = data["current_index"]
#     user_id = data["user_id"]
#     bot_id = data["bot_id"]
#     test_type_id = data["test_type_id"]
#     test_user_answer_id = data["test_user_answer_id"]

#     if current_index >= len(questions):
#         # На случай, если пользователь нажал кнопку позже
#         await callback.answer("Вопросов больше нет.")
#         return

#     question_id = questions[current_index]

#     # Извлекаем ответ (после «ans:»)
#     user_answer = callback.data.split("ans:")[1]

#     # Сохраняем ответ в JSON в одной записи TestUserAnswer
#     async with AsyncSessionLocal() as session:
#         test_user_answer = await session.get(TestUserAnswer, test_user_answer_id)
#         answers_dict = json.loads(test_user_answer.answer)
#         answers_dict[str(question_id)] = user_answer
#         test_user_answer.answer = json.dumps(answers_dict, ensure_ascii=False)
#         await session.commit()

#     # Двигаемся к следующему вопросу
#     current_index += 1
#     await state.update_data(current_index=current_index)

#     # Уведомим Telegram, что коллбэк обработан
#     await callback.answer()

#     # Добавим отображение "галочки" на выбранной кнопке:
#     async with AsyncSessionLocal() as session:
#         question_obj = await session.get(TestQuestion, question_id)
#         if question_obj.question_type == "rating":
#             answers_list = [str(i) for i in range(1, 11)]
#         else:
#             answers_list = []
#             if question_obj.possible_answers:
#                 answers_list = json.loads(question_obj.possible_answers)

#     # Перерисовываем клавиатуру, отмечая выбранный
#     buttons = []
#     for ans in answers_list:
#         prefix = "✅ " if ans == user_answer else ""
#         buttons.append([InlineKeyboardButton(text=prefix + str(ans), callback_data=f"ans:{ans}")])
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

#     try:
#         await callback.message.edit_reply_markup(reply_markup=keyboard)
#     except TelegramBadRequest as e:
#         if "message is not modified" in str(e):
#             pass
#         else:
#             raise

#     # Вызываем повторно логику запроса следующего вопроса
#     # Вместо message передаём callback.message
#     await ask_next_question(callback.message, state)


# @router.callback_query(F.data.startswith("mul:"))
# async def process_multiple_choice(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     selected_options = data.get("selected_options", [])
#     questions = data["questions"]
#     current_index = data["current_index"]
#     question_id = questions[current_index]

#     chosen_value = callback.data.split("mul:")[1]

#     if chosen_value in selected_options:
#         selected_options.remove(chosen_value)
#     else:
#         selected_options.append(chosen_value)

#     await state.update_data(selected_options=selected_options)

#     # Перестроим клавиатуру с чекмарками
#     async with AsyncSessionLocal() as session:
#         question_obj = await session.get(TestQuestion, question_id)
#         all_options = json.loads(question_obj.possible_answers)

#     buttons = []
#     for option in all_options:
#         prefix = "✅ " if option in selected_options else ""
#         buttons.append([InlineKeyboardButton(
#             text=prefix + option,
#             callback_data=f"mul:{option}"
#         )])
#     buttons.append([InlineKeyboardButton(text="Готово", callback_data="mul_done")])
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

#     try:
#         await callback.message.edit_reply_markup(reply_markup=keyboard)
#     except TelegramBadRequest as e:
#         if "message is not modified" in str(e):
#             pass
#         else:
#             raise
#     await callback.answer(f"Вы выбрали: {chosen_value}")

# @router.callback_query(F.data == "mul_done")
# async def process_multiple_choice_done(callback: types.CallbackQuery, state: FSMContext):
#     """
#     Пользователь нажал «Готово» — сохраняем набор выбранных вариантов и переходим дальше.
#     """
#     data = await state.get_data()
#     questions = data["questions"]
#     current_index = data["current_index"]
#     user_id = data["user_id"]
#     bot_id = data["bot_id"]
#     test_type_id = data["test_type_id"]
#     test_user_answer_id = data["test_user_answer_id"]
#     selected_options = data.get("selected_options", [])

#     if current_index >= len(questions):
#         await callback.answer("Вопросов больше нет.")
#         return

#     question_id = questions[current_index]
#     user_answer = selected_options

#     # Сохраняем ответ в JSON в одной записи TestUserAnswer
#     async with AsyncSessionLocal() as session:
#         test_user_answer = await session.get(TestUserAnswer, test_user_answer_id)
#         answers_dict = json.loads(test_user_answer.answer)
#         answers_dict[str(question_id)] = user_answer
#         test_user_answer.answer = json.dumps(answers_dict, ensure_ascii=False)
#         await session.commit()

#     current_index += 1
#     await state.update_data(current_index=current_index, selected_options=[])
#     await callback.answer()
#     await ask_next_question(callback.message, state)