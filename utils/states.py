

from aiogram.dispatcher.filters.state import State, StatesGroup


class TaskState(StatesGroup):
    task_select = State(),
    task_name = State()

class RegisterState(StatesGroup):  
    group_select = State()  # Статус - выбор группы
    sub = State() #Уведомление
    complete = State()