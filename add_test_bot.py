import asyncio
import json
from app.db.database import AsyncSessionLocal
from app.db.models import BotToken, TestType, TestQuestion
from sqlalchemy import select

async def add_test_bot():
    async with AsyncSessionLocal() as session:
        # 1. Проверяем, существует ли уже тестовый бот
        existing_bot = (await session.execute(select(BotToken).where(BotToken.token == "7940354996:AAHIuj74SB5TBfobLKt83X4ZwI1M0ENF7t0"))).scalar_one_or_none()
        if existing_bot:
            print("Тестовый бот уже существует в базе данных.")
            return

        # 2. Добавляем тестового бота
        new_bot = BotToken(
            name="Test Bot",
            token="7940354996:AAHIuj74SB5TBfobLKt83X4ZwI1M0ENF7t0",  # Замените на реальный токен
            is_active=True,
            owner_name="Иван Иванов",  # ФИО владельца
            owner_telegram_username="ivan_telegram"  # Опциональный никнейм
        )
        session.add(new_bot)
        await session.commit()
        print("Тестовый бот добавлен в базу данных.")

        # 3. Проверяем, существует ли уже тип теста для этого бота
        existing_test_type = (await session.execute(select(TestType).where(TestType.bot_id == new_bot.id))).scalar_one_or_none()
        if existing_test_type:
            print("Тип теста уже существует для этого бота.")
            return

        # 4. Добавляем тип теста
        test_type = TestType(
            name="Демо-тест",
            description="Тестовый опросник для демонстрации",
            bot_id=new_bot.id
        )
        session.add(test_type)
        await session.commit()
        print("Тип теста добавлен в базу данных.")

        # 5. Проверяем, существуют ли уже вопросы для этого типа теста
        existing_questions = (await session.execute(select(TestQuestion).where(TestQuestion.test_type_id == test_type.id))).scalars().all()
        if existing_questions:
            print("Вопросы уже существуют для этого типа теста.")
            return

        # 6. Добавляем тестовые вопросы
        questions = [
            {
                "question_text": "Как вас зовут?",
                "question_type": "text",
                "possible_answers": None
            },
            {
                "question_text": "Выберите один вариант ответа:",
                "question_type": "single_choice",
                "possible_answers": json.dumps(["Вариант 1", "Вариант 2", "Вариант 3"], ensure_ascii=False)
            },
            {
                "question_text": "Оцените по шкале от 1 до 10:",
                "question_type": "rating",
                "possible_answers": None
            },
            {
                "question_text": "Выберите несколько вариантов ответа:",
                "question_type": "multiple_choice",
                "possible_answers": json.dumps(["Опция A", "Опция B", "Опция C"], ensure_ascii=False)
            },
            {
                "question_text": "Введите ваш возраст:",
                "question_type": "int",
                "possible_answers": None
            }
        ]

        for q_data in questions:
            question = TestQuestion(
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                possible_answers=q_data["possible_answers"],
                is_active=True,
                test_type_id=test_type.id,
                bot_id=new_bot.id
            )
            session.add(question)
        await session.commit()
        print("Тестовые вопросы добавлены в базу данных.")

if __name__ == "__main__":
    asyncio.run(add_test_bot()) 