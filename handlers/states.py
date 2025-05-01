from aiogram.fsm.state import StatesGroup, State # type: ignore

class NewsStates(StatesGroup):
    title = State()
    content = State()
    image = State()

class CreateGroupStates(StatesGroup):
    group_name = State()

class DeleteGroupStates(StatesGroup):
    group_name = State()

class ScheduleStates(StatesGroup):
    select_group = State()
    image = State()

class DeleteScheduleStates(StatesGroup):
    select_group = State()

class AnswerTheQuestion(StatesGroup):
    start = State()
    answer = State()

class StartStates(StatesGroup):
    group_name = State()

class SelectGroupStates(StatesGroup):
    group_name = State()

class AskQuestionStates(StatesGroup):
    get_question = State()

class AnswerStates(StatesGroup):
    waiting_for_answer = State()

class AdminStates(StatesGroup):
    waiting_for_admin_id = State()

class AdminScheduleStates(StatesGroup):
    select_group = State()