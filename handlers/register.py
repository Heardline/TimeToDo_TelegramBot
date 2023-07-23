from utils.states import RegisterState
from utils.db.db import Group, Student
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from sqlalchemy import select

from utils.func import get_student
from config import Settings

# Чтение приветственного сообщения и сообщения группы
with open(Settings.cmd_welcome, 'r', encoding='utf-8') as file:
    WELCOME_MESSAGE = file.read()
with open(Settings.cmd_group, 'r', encoding='utf-8') as file:
    GROUP_MESSAGE = file.read()

# Получение сессии базы данных
def get_db_session(bot):
    return bot.get('db')

# Обработка команды /start
async def send_welcome(message: types.Message, state: FSMContext):
    db_session = get_db_session(message)
    async with db_session() as session:
        student = await get_student(session, message.from_user.id)
        if not student:
            # Если студент не найден, начинаем процесс регистрации
            telegram_id = message.from_user.id
            await state.update_data(telegram_id=telegram_id)
            await RegisterState.group_select.set()
            await message.reply(WELCOME_MESSAGE, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.answer("<b> Привет, рад тебя видеть снова </b>", parse_mode='HTML', disable_web_page_preview=True)

# Выбор группы студента
async def select_group(message: types.Message, state: FSMContext):
    db_session = get_db_session(message)
    async with db_session() as session:
        sql = select(Group).where(Group.name == message.text)
        request = await session.execute(sql)
        group = request.scalar_one_or_none()

        if group:
            await state.update_data(group=message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Да", "Нет")
            await message.answer(GROUP_MESSAGE, parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)
            await RegisterState.next()
        else:
            await message.reply("Что-то пошло не так, проверь, чтобы группа была формата ГИБО-05-19. Если не получается, значит база данных не доступна либо ваша группа не загружена.", parse_mode='HTML', disable_web_page_preview=True)

# Настройка уведомлений за 20 минут
async def select_notify(message: types.Message, state: FSMContext):
    db_session = get_db_session(message)
    async with db_session() as session:
        data = await state.get_data()
        notify = message.text == "Да"
        student = Student(telegram_id=data['telegram_id'], grp=data['group'], notify=notify)
        session.add(student)
        await session.commit()
    await state.finish()
    await menu(message)
