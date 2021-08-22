
from service.vk_parser.vk_main import get_last_posts
from handlers.admin import update_data
import utils.time_lessons as time_lesson
from aiogram import Dispatcher, types

from utils.simple_calendar import calendar_callback
from utils.states import TaskState, RegisterState
from handlers.menu import menu
from handlers.register import (
    select_group, select_notify, send_welcome
)
from handlers.schedul_lesson import (
    scheduler_today, scheduler_tomorrow, scheduler_week
)
from handlers.task import (
    process_simple_calendar, task, task_add,
    task_add_handler, task_callback, task_delete, task_done,
    task_name, task_select
)


# Хендлеры команды
def register_commands(dp: Dispatcher):
    '''dp.register_message_handler( , )'''
    # Регистрация
    dp.register_message_handler(send_welcome, commands="start"),
    dp.register_message_handler(select_group, state=RegisterState.group_select),
    dp.register_message_handler(select_notify, state=RegisterState.sub),

    # Меню + настройки
    dp.register_message_handler(menu, commands="menu"),
    #dp.register_message_handler( , )

    # Расписание
    dp.register_message_handler(scheduler_today,commands='today'),
    dp.register_message_handler(scheduler_tomorrow,commands='tomorrow'),
    dp.register_message_handler(scheduler_week,commands='week'),

    # Задачи
    dp.register_message_handler(task_add,commands='addtask'),
    dp.register_message_handler(task,commands='task'),
    dp.register_message_handler(task_name, state=TaskState.task_name),
    dp.register_message_handler(task_select, state=TaskState.task_select),
    
    # Кастомные команды
    dp.register_message_handler(update_data,commands='update'),
    dp.register_message_handler(get_posts,commands='test')

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_simple_calendar, calendar_callback.filter()),
    dp.register_callback_query_handler(task_done, task_callback.filter(act='done')),
    dp.register_callback_query_handler(task_delete, task_callback.filter(act='delete')),
    dp.register_callback_query_handler(task_add_handler, task_callback.filter(act='add'))
    #dp.register_callback_query_handler(task_update, task_callback.filter(act='update')),

async def get_posts(message: types.Message):
    await get_last_posts(message)


