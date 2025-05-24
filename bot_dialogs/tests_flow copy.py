# from aiogram.types import CallbackQuery
# from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
# from aiogram_dialog.widgets.kbd import Button
# from aiogram_dialog.widgets.text import Format, Const
# from aiogram_dialog.widgets.input import MessageInput
# from sqlalchemy import select
# from db import AsyncSessionLocal
# from models import TestQuestion, TestUserAnswer
# from .states import TestsSG
# from aiogram.types import CallbackQuery
# from aiogram_dialog import DialogManager, ShowMode, StartMode

# async def on_test_type_click(c: CallbackQuery, widget, manager: DialogManager, item: str):
#     print(f"🌀 📝 Тестирование нажата {item}")
#     # Записываем выбранный test_type_id и загружаем список вопросов
#     test_type_id = int(item)
#     async with AsyncSessionLocal() as session:
#         res = await session.execute(
#             select(TestQuestion).where(
#                 TestQuestion.test_type_id == test_type_id,
#                 TestQuestion.is_active == True
#             ).order_by(TestQuestion.id)
#         )
#         questions = res.scalars().all()
#     # Инициализируем запись результатов
#     async with AsyncSessionLocal() as session:
#         ans = TestUserAnswer(
#             user_id=manager.dialog_data["user_id"],
#             test_type_id=test_type_id,
#             bot_id=manager.event.bot.id,
#             answer="{}"
#         )
#         session.add(ans)
#         await session.commit()
#         await session.refresh(ans)
#     # Поднимаем данные в dialog_data
#     await manager.dialog_data.update({
#         "questions": [q.id for q in questions],
#         "current_index": 0,
#         "test_user_answer_id": ans.id,
#         "test_type_id": test_type_id,
#     })
#     # Переходим к первому вопросу
#     await manager.start(
#         TestsSG.QUESTION,
#         mode=StartMode.RESET_STACK,
#         show_mode=ShowMode.SEND,
#         data={"test_type_id": test_type_id, **manager.dialog_data},
#     )

# async def get_current_question_data(manager: DialogManager, **kwargs):
#     idx = manager.dialog_data["current_index"]
#     q_id = manager.dialog_data["questions"][idx]
#     async with AsyncSessionLocal() as session:
#         q = await session.get(TestQuestion, q_id)
#     return {
#         "question_text": q.question_text,
#         "question_type": q.question_type,
#         "possible_answers": q.possible_answers or "",
#     }

# async def on_user_answer(message: str, widget, manager: DialogManager):
#     data = manager.dialog_data
#     idx = data["current_index"]
#     q_id = data["questions"][idx]
#     ans_id = data["test_user_answer_id"]
#     # Сохраняем ответ
#     async with AsyncSessionLocal() as session:
#         ua = await session.get(TestUserAnswer, ans_id)
#         answers = {} if not ua.answer else __import__("json").loads(ua.answer)
#         answers[str(q_id)] = message
#         ua.answer = __import__("json").dumps(answers, ensure_ascii=False)
#         await session.commit()
#     # Переходим к следующему вопросу или завершаем
#     if idx + 1 < len(data["questions"]):
#         await manager.dialog_data.update({"current_index": idx + 1})
#         await manager.switch_to(TestsSG.QUESTION)
#     else:
#         await manager.done()  # закрывает диалог

# test_selection_window = Window(
#     Const("Выберите тип тестирования:"),
#     # сюда уже должен быть подключён ваш существующий Select c on_test_type_click
#     state=TestsSG.MAIN,
# )

# question_window = Window(
#     Format("Вопрос {dialog_data[current_index]+1}: {question_text}"),
#     # Если нужен свободный ввод:
#     MessageInput(on_user_answer),
#     # Для простых вариантов можно добавить кнопки, например:
#     # Button(Format("{item}"), id="opt", on_click=on_user_answer) 
#     getter=get_current_question_data,
#     state=TestsSG.QUESTION,
# )

# tests_dialog = Dialog(
#     test_selection_window,
#     question_window,
# )