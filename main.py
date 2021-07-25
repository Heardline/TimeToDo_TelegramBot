import asyncio

import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from numpy import exp
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aioschedule

from config import db,Auth
from commands import register_commands,register_callbacks
from utils.db.base import Base

#pdb.update_data()
API_TOKEN = Auth.API_TOKEN
# Команды для подсказок телеграма
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="today", description="Расписание на сегодня"),
        BotCommand(command="tomorow", description="Расписаниие на завтра"),
        BotCommand(command="week", description="Расписание на этой неделе")
    ]
    await bot.set_my_commands(commands)
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
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    bot = Bot(API_TOKEN, parse_mode="HTML")
    bot["db"] = async_session
    dp = Dispatcher(bot,storage=MemoryStorage())

    register_commands(dp)
    register_callbacks(dp)

    await set_bot_commands(bot)
    
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

# Уведомлялки утром
'''async def notif_morning():
    for user in UsersDB.find({"sub":"True"}):
        #try:
        group = UsersDB.find_one({"chat_id":user["chat_id"]})["group"]
        Lesson = "<b> Доброе утро! </b> \n "
        a = 0 #Локальная переменная - формирует адрес исходя из четной/нечетной неделе и когда.
        if time_lesson.NumberOfMonth() % 2 == 0:
            a = 1
        if pdb.get_lesson(time_lesson.todayIs()+1+a,group) == "nan":
            Lesson = Lesson + " <code> Ты везунчик, можешь немного поспать, к первой не надо. </code> \n"
            if pdb.get_lesson(time_lesson.todayIs()+3+a,group) == "nan":
                Lesson = Lesson + "Ко второй тоже. Вообще топ.\n"
        a = 0
        Lesson = Lesson + "Сегодня у тебя: \n"
        check_lesson = False
        for i in range(1,7):
            if time_lesson.NumberOfMonth() % 2 == 0: 
                 a = i*2
            else:
                a = (i*2)-1
             # Четная/ не четная неделя
            if pdb.get_lesson(time_lesson.todayIs()+a,group) == "nan":
                pass
            else: 
                check_lesson = True
                Lesson = pdb.ready_lesson(Lesson,group,a,i)
        if check_lesson is False:
            Lesson = "<b>Сегодня нету пар </b> ✨🎉\n Спи спокойно и иди гуляй)"       
        await bot.send_message(user["chat_id"], Lesson, parse_mode='HTML', disable_web_page_preview=True)

# Уведомлять после каждой пары
async def notif_every_lesson():
    for user in UsersDB.find({"sub":"True"}):
        #try:
        group = UsersDB.find_one({"chat_id":user["chat_id"]})["group"]
        Lesson = "<b> У тебя по расписанию дальше: </b> \n "
        a = 0 #Локальная переменная - формирует адрес исходя из четной/нечетной неделе и когда.
        now = time_lesson.convertHourtoLesson()
        if pdb.get_lesson(time_lesson.todayIs()+1+now,group) == "nan":
            break
        if time_lesson.NumberOfMonth() % 2 == 0: 
            a = now*2
        else:
            a = (now*2)-1
             # Четная/ не четная неделя
        if pdb.get_lesson(time_lesson.todayIs()+a,group) == "nan":
            pass
        else: 
            Lesson = pdb.ready_lesson(Lesson,group,a,now)     
        await bot.send_message(user["chat_id"], Lesson, parse_mode='HTML', disable_web_page_preview=True)
       
async def scheduler():
    aioschedule.every().day.at("8:40").do(notif_morning)
    aioschedule.every().day.at("10:30").do(notif_every_lesson)
    aioschedule.every().day.at("12:30").do(notif_every_lesson)
    aioschedule.every().day.at("14:10").do(notif_every_lesson)
    aioschedule.every().day.at("16:10").do(notif_every_lesson)
    aioschedule.every().day.at("17:50").do(notif_every_lesson)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(5)

async def on_startup(x):
    asyncio.create_task(scheduler())
'''
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")   

