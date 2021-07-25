import datetime
from importlib.metadata import requires
import os
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.sql.expression import text
import config
from aiogram import types, Dispatcher
from aiogram.types import CallbackQuery, reply_keyboard
from sqlalchemy import select,insert, and_,update
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, inline_keyboard
import utils.task_manager as task_manager
from utils.simple_calendar import calendar_callback, SimpleCalendar
from utils.db.db import Student, Group, Lesson, Task, import_from_xlsx
import utils.time_lessons as time_lesson

#Переключение пользователя
class Status(StatesGroup):  
    group_select = State()  # Статус - выбор группы
    sub = State() #Уведомление
    complete = State()
    task_name = State() #Проверка авторизации 
    task_select = State()

async def get_student(db_session, user_id: int) -> Student:
    sql = select(Student).where(Student.telegram_id == user_id)
    request = await db_session.execute(sql)
    player: Student = request.scalar()
    return player

task_callback = CallbackData('task_act','id','act')

async def send_welcome(message: types.Message,state: FSMContext):
    db_session = message.bot.get('db')
    # Проверяем есть ли в базе студент
    async with db_session() as session:
        student = await get_student(session,message.from_user.id)
        if not student:
            async with state.proxy() as data:
                data['telegram_id'] = message.from_user.id
            await Status.group_select.set()
            with open(config.FileLocation.cmd_welcome, 'r', encoding='utf-8') as file:
                await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.answer("<b> Привет, рад тебя видеть снова </b>", parse_mode='HTML', disable_web_page_preview=True)
            await menu(message)

# Внесение группы  
async def select_group(message: types.Message,state: FSMContext):
    db_session = message.bot.get('db')
    sql = select(Group).where(Group.name == message.text)
    async with db_session() as session:
        request = await session.execute(sql)
        group = request.scalar()
        if group:
            async with state.proxy() as data:
                data['group'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Да", "Нет")
            with open(config.FileLocation.cmd_group,'r', encoding='utf-8') as file:
                await message.answer(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)
            await Status.next()
        else:
            await message.reply("Что-то пошло не так, проверь, чтобы группа была формата ГИБО-05-19. Если не получается, значит база данных не доступна либо ваша группа не загружена.", parse_mode='HTML', disable_web_page_preview=True)

# Настройка Уведомление за 20 минут
async def select_notify(message: types.Message,state: FSMContext):
    db_session = message.bot.get('db')
    async with db_session() as session:
        async with state.proxy() as data:
            if message.text=="Да": notify = True 
            else: notify = False
            student = Student(telegram_id=data['telegram_id'],grp=data['group'],notify=notify)
        session.add(student)
        await session.commit()
    markup = types.ReplyKeyboardRemove()
    await state.finish()
    await menu(message)
    # Конец регистрации

# Главное меню
async def menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Сегодня ⏲", "Завтра 📆", "Неделя 📅","Мои задачи 📋","Настройки 🛠")
    with open(config.FileLocation.cmd_menu,'r', encoding='utf-8') as file:
            await message.answer(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)

# Пары на сегодня
async def scheduler_today(message: types.Message):
    Lesson_text = f"<b> {time_lesson.TodayToEmoji(0)} | {time_lesson.NumberOfMonth()} неделя. </b> \n" 
    db_session = message.bot.get('db')
    async with db_session() as session:
        # Четная/ не четная неделя
        if time_lesson.NumberOfMonth() % 2 == 0: 
            week=0 
        else: 
            week=1 
        student = await get_student(session,message.from_user.id)
        group = student.grp
        sql = select(Lesson).where(and_(Lesson.grp == group, Lesson.day == time_lesson.todayIs(), Lesson.week == week))
        request = await session.execute(sql)
        lessons = request.scalars()
        k=0
        for lesson in lessons:
            Lesson_text+=(f"{time_lesson.NumberToEmoji(lesson.time//2)}\n {lesson.name} |  {lesson.type} | {lesson.room} \n {lesson.teacher} \n")
            k+=1
        if k==0:
            Lesson_text = "<b>Сегодня нету пар </b> ✨🎉\n"
    await message.answer(Lesson_text, parse_mode='HTML', disable_web_page_preview=True)

## Пары на завтра
async def scheduler_tomorrow(message: types.Message):
    Lesson_text = f"<b> {time_lesson.TodayToEmoji(1)} | {time_lesson.NumberOfMonth()} неделя. </b> \n" 
    db_session = message.bot.get('db')
    async with db_session() as session:
        # Четная/ не четная неделя
        if time_lesson.NumberOfMonth() % 2 == 0: week=0 
        else: week=1 
        student = await get_student(session,message.from_user.id)
        group = student.grp
        sql = select(Lesson).where(and_(Lesson.grp == group, Lesson.day == (time_lesson.todayIs()+1)%7, Lesson.week == week))
        request = await session.execute(sql)
        lessons = request.scalars()  
        k = 0
        for lesson in lessons:
            Lesson_text+=(f"{time_lesson.NumberToEmoji(lesson.time // 2)}\n {lesson.name} |  {lesson.type} | {lesson.room} \n {lesson.teacher} \n")
            k+=1
        if k==0:
            Lesson_text = "<b>Завтра нету пар </b> ✨🎉\n)"
    await message.answer(Lesson_text, parse_mode='HTML', disable_web_page_preview=True)

## Пары на эту неделю
async def scheduler_week(message: types.Message):
    Lesson_text = f" <b>Расписание на {time_lesson.NumberOfMonth()} неделю. </b> \n \n" 
    db_session = message.bot.get('db')
    async with db_session() as session:
        # Четная/ не четная неделя
        if time_lesson.NumberOfMonth() % 2 == 0: week=0 
        else: week=1 
        student = await get_student(session,message.from_user.id)
        group = student.grp
        for day in range(1,7):
            Lesson_text += f"<b> {time_lesson.TodayToEmoji(day)} \n </b> "
            sql = select(Lesson).where(and_(Lesson.grp == group, Lesson.day == (time_lesson.todayIs()+day)%7, Lesson.week == week))
            request = await session.execute(sql)
            lessons = request.scalars()  
            k = 0
            for lesson in lessons:
                Lesson_text+=(f"{time_lesson.NumberToEmoji((lesson.time+1) // 2)}\n {lesson.name} |  {lesson.type} | {lesson.room} {lesson.teacher} \n")
                k+=1
            if k==0:
                Lesson_text += f"<b>Нету пар </b> ✨\n"
            Lesson_text += '\n'
    await message.answer(Lesson_text, parse_mode='HTML', disable_web_page_preview=True)

async def task(message: types.Message):
    inline_button_add = InlineKeyboardButton('Добавить задачу 📋', callback_data=task_callback.new(0,'add'))
    inline_button_remove_all = InlineKeyboardButton('Удалить все 💥', callback_data=task_callback.new(0,'remove_all'))
    inline_task = InlineKeyboardMarkup().row(inline_button_add,inline_button_remove_all)
    await message.answer('<b> 💡 Твои задачи </b>', parse_mode='HTML',reply_markup=inline_task)
    db_session = message.bot.get('db')
    async with db_session() as session:
        sql = select(Task).where(Task.student == message.from_user.id)
        request = await session.execute(sql)
        tasks = request.scalars()
        k = 0
        for task in tasks:
            k+=1
            inline_task = InlineKeyboardMarkup()
            if task.status != 'Готово':
                inline_task.insert(InlineKeyboardButton('Выполнено✅', callback_data=task_callback.new(task.id,'done')))
            inline_task.insert(InlineKeyboardButton('Удалить💥', callback_data=task_callback.new(task.id,'delete')))
            inline_task.insert(InlineKeyboardButton('Изменить⚙', callback_data=task_callback.new(task.id,'change')))
            await message.answer(f"<b> {time_lesson.emojiStatus[task.status]} {task.lesson} | {task.name} | Срок до {time_lesson.emojiToday[task.time.weekday()+1]} - {task.time.strftime('%d.%m.%y')} \n {task.desc} </b> " , parse_mode='HTML', reply_markup=inline_task)
        if k==0:
            await message.answer("Пока что у тебя нету задач" , parse_mode='HTML')
    
async def task_add(message: types.Message, state: FSMContext):
    await message.reply("До какого тебе нужно это сделать?",reply_markup= await SimpleCalendar().start_calendar())

async def task_name(message: types.Message,state: FSMContext):
    if message.text != 'Отмена':
        async with state.proxy() as data:
            data['lesson'] = message.text
            await Status.task_select.set()
            await message.answer("Лады, теперь напиши название задачи и через @ краткое описание (Сдать дз @ Надо сделать матан ст.25 №2,3,4)",reply_markup=types.ReplyKeyboardRemove())
    else:
        await state.finish()
        await message.answer("Отменено")

async def task_select(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        db_session = message.bot.get('db')
        async with db_session() as session:
            task = Task(name=message.text.split("@")[0],desc=message.text.split("@")[1],student=message.from_user.id,lesson=data['lesson'],time=data['time'],status='Не готово')
            session.add(task)
            await session.commit()
        await message.answer(f'Добавил задачу: {task.name} | {task.desc}',reply_markup=types.ReplyKeyboardRemove())
        await state.finish()

async def update_data(message: types.Message):
    await import_from_xlsx(message)

def register_commands(dp: Dispatcher):
    '''dp.register_message_handler( , )'''
    dp.register_message_handler(send_welcome, commands="start"),
    dp.register_message_handler(select_group, state=Status.group_select),
    dp.register_message_handler(select_notify, state=Status.sub),
    dp.register_message_handler(menu, commands="menu"),
    dp.register_message_handler(scheduler_today,commands='day'),
    dp.register_message_handler(scheduler_tomorrow,commands='tomorow'),
    dp.register_message_handler(scheduler_week,commands='week'),
    dp.register_message_handler(task_add,commands='addtask'),
    dp.register_message_handler(task,commands='task'),
    dp.register_message_handler(task_name,state=Status.task_name),
    dp.register_message_handler(task_select,state=Status.task_select),
    dp.register_message_handler(update_data,commands='update'),


''' CALLBACK BLOCK '''
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['time'] = date
            db_session = callback_query.message.bot.get('db')
            async with db_session() as session:
                student = await get_student(session,callback_query.message.chat.id)
                group = student.grp
                sql = select(Lesson).where(and_(Lesson.grp == group, Lesson.day==datetime.datetime.weekday(date)))
                request = await session.execute(sql)
                lessons = request.scalars()
                keyboard = ReplyKeyboardMarkup()
                keyboard.insert(InlineKeyboardButton('Другое'))
                for lesson in lessons:
                    keyboard.insert(InlineKeyboardButton(str(lesson.name)))
                keyboard.insert(InlineKeyboardButton('Отмена'))
                await callback_query.message.answer("Ок. А какая пара?", reply_markup=keyboard)
                await Status.task_name.set()

async def task_done(callback_query: CallbackQuery, callback_data: dict):
    db_session = callback_query.message.bot.get('db')
    async with db_session() as session:
        sql = update(Task).where(Task.id == int(callback_data['id'])).values(status='Готово')
        await session.execute(sql)
        await session.commit()
    await callback_query.message.edit_text('✅ ' + str(callback_query.message.text)[1:])

async def task_add_handler(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    await task_add(callback_query.message,state)

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_simple_calendar, calendar_callback.filter()),
    dp.register_callback_query_handler(task_done, task_callback.filter(act='done')),
    dp.register_callback_query_handler(task_add_handler, task_callback.filter(act='add'))
