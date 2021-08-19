
from admin import update_data
import utils.time_lessons as time_lesson
from aiogram import Dispatcher, types
from sqlalchemy import and_, select
from utils.db.db import Lesson, Student, import_from_xlsx
from utils.simple_calendar import calendar_callback

from menu import menu
from register import (
    RegisterState, select_group, select_notify, send_welcome
)
from schedul_lesson import (
    scheduler_today, scheduler_tomorrow, scheduler_week
)
from task import (
    TaskState, process_simple_calendar, task, task_add,
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
    dp.register_message_handler(scheduler_today,commands='day'),
    dp.register_message_handler(scheduler_tomorrow,commands='tomorrow'),
    dp.register_message_handler(scheduler_week,commands='week'),

    # Задачи
    dp.register_message_handler(task_add,commands='addtask'),
    dp.register_message_handler(task,commands='task'),
    dp.register_message_handler(task_name,state=TaskState.task_name),
    dp.register_message_handler(task_select,state=TaskState.task_select),
    
    # Кастомные команды
    dp.register_message_handler(update_data,commands='update'),

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_simple_calendar, calendar_callback.filter()),
    dp.register_callback_query_handler(task_done, task_callback.filter(act='done')),
    dp.register_callback_query_handler(task_delete, task_callback.filter(act='delete')),
    dp.register_callback_query_handler(task_add_handler, task_callback.filter(act='add'))
    #dp.register_callback_query_handler(task_update, task_callback.filter(act='update')),

# Поиска студента в БД
async def get_student(bot):
    db_session = bot.get('db')
    async with db_session() as session:
        sql = select(Student).where(Student.notify == True)
        request = await session.execute(sql)
        return request.scalars()

# Передает семинар для оповещения
async def get_next_lesson(bot,telegram_id):
    db_session = bot.get('db')
    async with db_session() as session:
        student = await get_student(session,telegram_id)
        group = student.grp
        if time_lesson.NumberOfMonth() % 2 == 0: week=0 
        else: week=1 
        sql = select(Lesson).where(and_(Lesson.grp == group, time_lesson.todayIs(), Lesson.week == week, Lesson.time == time_lesson.convertHourtoLesson))
        request = await session.execute(sql)
        return request.scalar()


