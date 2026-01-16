from aiogram.fsm.state import State, StatesGroup

class QuizStates(StatesGroup):
    waiting_for_start = State()
    publications = State()
    citations = State()
    membership = State()
    media = State()
    awards = State()
    leadership = State()
    salary = State()

    waiting_for_results = State()
