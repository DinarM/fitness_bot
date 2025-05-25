from sqlalchemy import BigInteger, Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func, Table, select
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

    # Связь "один-ко-многим" с TestQuestion
    questions = relationship("TestQuestion", back_populates="test_type")


class TestQuestion(BaseModel):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True)
    question_text = Column(Text, nullable=False)
    # possible_answers = Column(Text)  # Можно хранить JSON
    question_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    test_type_id = Column(Integer, ForeignKey("test_types.id"))
    order = Column(Integer, default=0)
    test_type = relationship("TestType", back_populates="questions")
    answers = relationship("TestAnswer", back_populates="question")


user_bots = Table(
    "user_bots",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("bot_id", Integer, ForeignKey("bot_tokens.id"), primary_key=True)
)

class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    telegram_username = Column(String(100))
    telegram_id = Column(BigInteger, nullable=False, unique=True, comment="ID Telegram пользователя")
    is_active = Column(Boolean, default=True, comment="Активен ли пользователь")
    is_admin = Column(Boolean, default=False, comment="Является ли пользователь администратором")
    
    answers = relationship("TestUserAnswer", back_populates="user")
    bots = relationship("BotToken", secondary=user_bots, back_populates="users")


class TestUserAnswer(BaseModel):
    __tablename__ = "test_user_answers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    test_type_id = Column(Integer, ForeignKey("test_types.id"), nullable=False)
    answer = Column(Text, nullable=False)
    bot_id = Column(Integer, ForeignKey("bot_tokens.id"), nullable=False)

    bot = relationship("BotToken")
    user = relationship("User", back_populates="answers")


class BotToken(BaseModel):
    __tablename__ = "bot_tokens"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, comment="Название или описание бота")
    token = Column(String(255), nullable=False, unique=True, comment="Токен Telegram-бота")
    telegram_bot_id = Column(BigInteger, nullable=True, unique=True, comment="ID Telegram бота")
    bot_username = Column(String(100), nullable=True, comment="Юзернейм Telegram бота")
    is_active = Column(Boolean, default=True, comment="Активен ли бот")
    owner_name = Column(String(255), nullable=False, comment="ФИО владельца бота")
    owner_telegram_username = Column(String(100), nullable=True, comment="Никнейм владельца в Telegram")
    users = relationship("User", secondary=user_bots, back_populates="bots")

class TestAnswer(BaseModel):
    __tablename__ = "test_answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    # is_correct = Column(Boolean, default=False)
    order = Column(Integer, default=0)


    question = relationship("TestQuestion", back_populates="answers")