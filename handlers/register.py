
from states import RegisterState
from utils.db.db import Group, Student
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from sqlalchemy import select

from commands import get_student, menu
from config import Settings

# /start

async def send_welcome(message: types.Message, state: FSMContext):
    db_session = message.bot.get('db')
    # Проверяем есть ли в базе студент
    async with db_session() as session:
        student = await get_student(session, message.from_user.id)
        if not student:
            async with state.proxy() as data:
                data['telegram_id'] = message.from_user.id
            await RegisterState.group_select.set()
            # Спрашиваем группу
            with open(Settings.cmd_welcome, 'r', encoding='utf-8') as file:
                await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.answer("<b> Привет, рад тебя видеть снова </b>", parse_mode='HTML', disable_web_page_preview=True)
            await menu(message)

# Внесение группы

async def select_group(message: types.Message, state: FSMContext):
    db_session = message.bot.get('db')
    sql = select(Group).where(Group.name == message.text)
    async with db_session() as session:
        request = await session.execute(sql)
        group = request.scalar()
        if group:
            async with state.proxy() as data:
                data['group'] = message.text
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, selective=True)
            markup.add("Да", "Нет")
            with open(Settings.cmd_group, 'r', encoding='utf-8') as file:
                await message.answer(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)
            await RegisterState.next()
        else:
            await message.reply("Что-то пошло не так, проверь, чтобы группа была формата ГИБО-05-19. Если не получается, значит база данных не доступна либо ваша группа не загружена.", parse_mode='HTML', disable_web_page_preview=True)

# Настройка Уведомление за 20 минут

async def select_notify(message: types.Message, state: FSMContext):
    db_session = message.bot.get('db')
    async with db_session() as session:
        async with state.proxy() as data:
            if message.text == "Да":
                notify = True
            else:
                notify = False
            student = Student(
                telegram_id=data['telegram_id'], grp=data['group'], notify=notify)
        session.add(student)
        await session.commit()
    await state.finish()
    await menu(message)
