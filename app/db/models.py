from sqlalchemy import BigInteger, Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    __abstract__ = True

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, comment="Дата удаления (если используется мягкое удаление)")

class TestType(BaseModel):
    __tablename__ = "test_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    bot_id = Column(Integer, ForeignKey("bot_tokens.id"), nullable=False)
    bot = relationship("BotToken")
    allow_multiple_passes = Column(Boolean, default=True, nullable=False, comment="Можно ли проходить тест несколько раз")
    estimated_duration = Column(Integer, nullable=True, comment="Примерная продолжительность прохождения теста в минутах")

    questions = relationship("TestQuestion", back_populates="test_type")


class TestQuestion(BaseModel):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    test_type_id = Column(Integer, ForeignKey("test_types.id"))
    order = Column(Integer, default=0)
    test_type = relationship("TestType", back_populates="questions")
    answers = relationship("TestAnswer", back_populates="question")


class UserBot(BaseModel):
    __tablename__ = "user_bots"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    bot_id = Column(Integer, ForeignKey("bot_tokens.id"), primary_key=True)
    is_admin = Column(Boolean, default=False)

    user = relationship("User", back_populates="user_bots")
    bot = relationship("BotToken", back_populates="user_bots")


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    last_name = Column(String(255))
    telegram_username = Column(String(100))
    telegram_id = Column(BigInteger, nullable=False, unique=True, comment="ID Telegram пользователя")
    is_active = Column(Boolean, default=True, comment="Активен ли пользователь")
    
    answers = relationship("TestUserAnswer", back_populates="user")
    user_bots = relationship("UserBot", back_populates="user")


class TestUserAnswer(BaseModel):
    __tablename__ = "test_user_answers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    test_type_id = Column(Integer, ForeignKey("test_types.id"), nullable=False)
    answers = Column(Text, nullable=False)
    bot_id = Column(Integer, ForeignKey("bot_tokens.id"), nullable=False)

    bot = relationship("BotToken")
    user = relationship("User", back_populates="answers")


class BotToken(BaseModel):
    __tablename__ = "bot_tokens"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, comment="Название или описание бота")
    token_hash = Column(String(255), unique=False, comment="Токен Telegram-бота")
    telegram_bot_id = Column(BigInteger, nullable=True, unique=True, comment="ID Telegram бота")
    bot_username = Column(String(100), nullable=True, comment="Юзернейм Telegram бота")
    is_active = Column(Boolean, default=True, comment="Активен ли бот")
    owner_name = Column(String(255), nullable=False, comment="ФИО владельца бота")
    owner_telegram_username = Column(String(100), nullable=True, comment="Никнейм владельца в Telegram")
    user_bots = relationship("UserBot", back_populates="bot")

class TestAnswer(BaseModel):
    __tablename__ = "test_answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, default=0)


    question = relationship("TestQuestion", back_populates="answers")