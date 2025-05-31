from aiogram.fsm.state import State, StatesGroup
class Main(StatesGroup):
    MAIN = State()

class Admin(StatesGroup):
    MAIN = State()

class Users(StatesGroup):
    MAIN = State()

class Tests(StatesGroup):
    MAIN = State()
    ROW = State()
    COLUMN = State()
    GROUP = State()


class TestsSG(StatesGroup):
    MAIN = State()      # выбор типа теста
    START_WINDOW = State() 
    TEXT_TYPE_WINDOW = State()
    SINGLE_CHOICE_TYPE_WINDOW = State()
    QUESTION = State()
    MULTIPLE_CHOICE_TYPE_WINDOW = State()
    NUMERIC_TYPE_WINDOW = State()
    RATING_TYPE_WINDOW = State()
    FINAL_REVIEW_WINDOW = State()  # добавляем новое состояние