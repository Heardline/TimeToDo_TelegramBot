
from datetime import datetime
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from sqlalchemy import select, delete, and_, update
from aiogram.dispatcher import FSMContext
from commands import get_student

from callback_data import task_callback
from states import TaskState
from utils.db.db import Lesson, Task
from aiogram import types
import utils.time_lessons as time_lesson
from simple_calendar import SimpleCalendar

# Меню задач

async def task(message: types.Message):
    inline_button_add = InlineKeyboardButton(
        'Добавить задачу 📋', callback_data=task_callback.new(0, 'add'))
    inline_button_remove_all = InlineKeyboardButton(
        'Удалить все 💥', callback_data=task_callback.new(0, 'remove_all'))
    inline_task = InlineKeyboardMarkup().row(
        inline_button_add, inline_button_remove_all)
    await message.answer('<b> 💡 Твои задачи </b>', parse_mode='HTML', reply_markup=inline_task)
    db_session = message.bot.get('db')
    async with db_session() as session:
        sql = select(Task).where(Task.student == message.from_user.id)
        request = await session.execute(sql)
        tasks = request.scalars()
        k = 0
        for task in tasks:
            k += 1
            inline_task = InlineKeyboardMarkup()
            # Если задача готова то не надо кнопки
            if task.status != 'Готово':
                inline_task.insert(InlineKeyboardButton(
                    'Выполнено✅', callback_data=task_callback.new(task.id, 'done')))
            inline_task.insert(InlineKeyboardButton(
                'Удалить💥', callback_data=task_callback.new(task.id, 'delete')))
            inline_task.insert(InlineKeyboardButton(
                'Изменить⚙', callback_data=task_callback.new(task.id, 'change')))
            await message.answer(f"<b> {time_lesson.emojiStatus[task.status]} {task.lesson} | {task.name} | {task.desc} \n Срок до {time_lesson.emojiToday[task.time.weekday()+1]} - {task.time.strftime('%d.%m.%y')} </b> \n ", parse_mode='HTML', reply_markup=inline_task)
        if k == 0:
            await message.answer("Пока что у тебя нету задач", parse_mode='HTML')

# Подменю - уточняем дату

async def task_add(message: types.Message):
    await message.reply("До какого тебе нужно это сделать?", reply_markup=await SimpleCalendar().start_calendar())

# Подменю - уточняем название задачи и описание

async def task_name(message: types.Message, state: FSMContext):
    if message.text != 'Отмена':
        async with state.proxy() as data:
            data['lesson'] = message.text
            await TaskState.task_select.set()
            await message.answer("Лады, теперь напиши название задачи и через @ краткое описание \
                (Сдать дз @ Надо сделать матан ст.25 №2,3,4)", reply_markup=types.ReplyKeyboardRemove())
    else:
        await state.finish()
        await message.answer("Отменено")

# Подменю - заносим данные

async def task_select(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        db_session = message.bot.get('db')
        async with db_session() as session:
            task = Task(name=message.text.split("@")[0], desc=message.text.split("@")[
                        1], student=message.from_user.id, lesson=data['lesson'], time=data['time'], status='Не готово')
            session.add(task)
            await session.commit()
        await message.answer(f'Добавил задачу: {task.name} | {task.desc}', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()


''' CALLBACK BLOCK '''

async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['time'] = date
            db_session = callback_query.message.bot.get('db')
            async with db_session() as session:
                student = await get_student(session, callback_query.message.chat.id)
                group = student.grp
                sql = select(Lesson).where(
                    and_(Lesson.grp == group, Lesson.day == datetime.datetime.weekday(date)))
                request = await session.execute(sql)
                lessons = request.scalars()
                keyboard = ReplyKeyboardMarkup()
                keyboard.insert(InlineKeyboardButton('Другое'))
                for lesson in lessons:
                    keyboard.insert(InlineKeyboardButton(str(lesson.name)))
                keyboard.insert(InlineKeyboardButton('Отмена'))
                await callback_query.message.answer("Ок. А какая пара?", reply_markup=keyboard)
                await TaskState.task_name.set()

# Кнопка отметки выполнения задачи

async def task_done(callback_query: CallbackQuery, callback_data: dict):
    db_session = callback_query.message.bot.get('db')
    async with db_session() as session:
        sql = update(Task).where(Task.id == int(
            callback_data['id'])).values(status='Готово')
        await session.execute(sql)
        await session.commit()
    await callback_query.message.edit_text('✅ ' + str(callback_query.message.text)[1:])

# Кнопка удаления задачи

async def task_delete(callback_query: CallbackQuery, callback_data: dict):
    db_session = callback_query.message.bot.get('db')
    async with db_session() as session:
        sql = delete(Task).where(Task.id == int(callback_data['id']))
        await session.execute(sql)
        await session.commit()
    await callback_query.message.delete()

# Кнопка изменения задачи
'''async def task_change(callback_query: CallbackQuery, callback_data: dict):
    db_session = callback_query.message.bot.get('db')
    async with db_session() as session:
'''

async def task_add_handler(callback_query: CallbackQuery, state: FSMContext):
    await task_add(callback_query.message, state)
