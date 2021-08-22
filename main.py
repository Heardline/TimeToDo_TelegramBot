import asyncio
from service.vk_parser.vk_main import check_new_post
from config import vk
import re
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import aioschedule
from handlers.commands import register_commands,register_callbacks
from utils.func import get_student,get_next_lesson, get_students
from utils.db.base import Base

# Проверка загрузки конфига
try:
    from config import db,Auth
except ModuleNotFoundError:
    logging.error(
        "Config file not found!\n Please create config.py file according to config.py.example")
    exit()
except ImportError as err:
    logging.error('Bot is not defined in the config file')
    exit()

#pdb.update_data()
API_TOKEN = Auth.API_TOKEN
# Команды для подсказок телеграма
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="today", description="Пары на сегодня"),
        BotCommand(command="tomorow", description="Пары на завтра"),
        BotCommand(command="week", description="Пары на этой неделе"),
        BotCommand(command="task", description="Мой задачи"),
        BotCommand(command="addtask", description="Добавить задачу"),
        BotCommand(command="sub", description="Настроить уведомления")
    ]
    await bot.set_my_commands(commands)


async def scheduler():
    aioschedule.every(10).minutes.do(send_new_post)
    aioschedule.every().day.at("8:20").do(alert_lesson)
    aioschedule.every().day.at("10:30").do(alert_lesson)
    aioschedule.every().day.at("12:30").do(alert_lesson)
    aioschedule.every().day.at("14:10").do(alert_lesson)
    aioschedule.every().day.at("16:10").do(alert_lesson)
    aioschedule.every().day.at("17:50").do(alert_lesson)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(5)

bot = Bot(API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot,storage=MemoryStorage())

# Логи + SQLAlchemy + aiogram + polling
async def main():
    logging.basicConfig(
        level=logging.INFO  ,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    engine = create_async_engine(
        f"postgresql+asyncpg://postgres:k686999@127.0.0.1/Schedul",
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False will prevent attributes from being expired
    # after commit.
    asyncio.create_task(scheduler())
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    bot["db"] = async_session

    register_commands(dp)
    register_callbacks(dp)
    await set_bot_commands(bot)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

# Уведомлялки за 10 минут до пары 
async def alert_lesson():
    students = await get_students(bot)
    for student in students:
        lesson = await get_next_lesson(bot,student.telegram_id)
        if lesson:
            await bot.send_message(student.telegram_id,f'💬 Через 10 минут начнется {lesson.name} {lesson.room} {lesson.type}',disable_notification=False)

# Уведомления о новом посте в группе ВК
async def send_new_post(posts,bot):
    if check_new_post('https://vk.com/sumirea'): 
        students = await get_students(bot) # Необходима отдельная функция и настройки уведомления для студентов с выбором группы ВК
        for student in students:
            for post in posts:
                if re.search(vk.blackword,post['text']):
                    pass
                else:
                    if post['media']:
                        await bot.send_message(student.telegram_id,post['text'] + '\n <a href="' + post['media']['photos'][0]+'">.</a>',parse_mode='HTML')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")   