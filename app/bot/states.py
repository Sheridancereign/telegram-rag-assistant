from aiogram.fsm.state import State, StatesGroup


class RagStates(StatesGroup):
    waiting_for_question = State()