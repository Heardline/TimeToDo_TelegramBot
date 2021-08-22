

from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterState(StatesGroup):  
    group_select = State()  # Статус - выбор группы
    sub = State() #Уведомление
    complete = State()
class TaskState(StatesGroup):
    task_name = State(),
    task_select = State()