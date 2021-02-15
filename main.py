
import os,sys,time
from aiogram.dispatcher.filters import state
import aiohttp
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from numpy import exp
from pymongo import MongoClient
import utils.scheduler as Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

import config
import utils.time_lessons as time_lesson

API_TOKEN = config.Auth.API_TOKEN

# Логи
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=API_TOKEN)
#storage = MongoStorage(host=config.MongoAuth.host, port=27017, db_name='users', username="admin", password=config.MongoAuth.password) #Не работает с библиотекой
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
#Инициализируем базу данных
client = MongoClient('mongodb+srv://admin:' + str(config.Auth.password_db) + "@cluster0.cy3ca.mongodb.net/", 27017)
db = client['Data']
UsersDB = db["Users"]
GroupDB = db["Group"]
Scheduler.get_pandas("")


def Check_Group(text):
    if GroupDB.find_one({"group":text}) is None:
       return False 
    else:
       return True

#Переключение пользователя
class Group(StatesGroup):  
    group_select = State()  # Статус - выбор группы
    sub = State() #Уведомление
    complete = State()  #Проверка авторизации

# Привествие пользователя
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if UsersDB.find_one({"chat_id":message.chat.id}) is None:
        await Group.group_select.set()
        with open(config.FileLocation.cmd_welcome, 'r', encoding='utf-8') as file:
            await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True)
    else:
        await bot.send_message(message.chat.id, "<b> Привет, рад тебя видеть снова </b>", parse_mode='HTML', disable_web_page_preview=True)
        await Group.complete.set()
        await menu(message)

# Внесение группы  
@dp.message_handler(state=Group.group_select)
async def select_group(message: types.Message):
    if Check_Group(message.text) is True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Да", "Нет")
        with open(config.FileLocation.cmd_group,'r', encoding='utf-8') as file:
            await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)
        await Group.sub.set()
        UsersDB.insert_one({"chat_id": message.chat.id, "group": message.text, "sub":"True"})
        
    else:
        await message.reply("Что-то пошло не так, проверь, чтобы группа была формата ГИБО-05-19. Если не получается, значит база данных не доступна либо ваша группа не загружена.", parse_mode='HTML', disable_web_page_preview=True)

# Настройка Уведомление за 20 минут
dp.message_handler(state=Group.sub)
async def select_sub(message: types.Message):
    if message.text == "Да":
        UsersDB.find_one_and_update({"chat_id":message.chat.id, "sub":"True" })
    else:
        UsersDB.find_one_and_update({"chat_id":message.chat.id, "sub":"False" })
    markup = types.ReplyKeyboardRemove()
    await Group.complete.set()
    await menu(message)
    # Конец регистрации

# Главное меню
dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("⏲Пары на сегодня", "📆На завтра", "📅На этой неделе","📋Мои задачи","🛠Настройки")
    with open(config.FileLocation.cmd_menu,'r', encoding='utf-8') as file:
            await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)
# Для тестов           
@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    await notif_morning()

# Пары на сегодня
@dp.message_handler(commands=['day','Пары на сегодня'])
async def scheduler_today(message: types.Message):
    Lessons = "<b> Пары на " + str(time_lesson.TodayToEmoji(0)) + str(time_lesson.NumberOfMonth()) + " неделя. </b> \n" 
    group = UsersDB.find_one({"chat_id":message.chat.id})["group"]
    check_lesson = False # Проверяет, есть ли вообще пары на сегодня
    for i in range(1,7):
        if time_lesson.NumberOfMonth() % 2 == 0: # Четная/ не четная неделя
            a = i*2
        else:
            a = (i*2)-1
        if Scheduler.get_lesson(time_lesson.todayIs()+a,group) == "nan" or " ":
            pass
        else: 
            check_lesson = True
            Lessons = Scheduler.ready_lesson(Lessons,group, a,i)  
    if check_lesson is False:
        Lessons = "<b>Сегодня нету пар </b> ✨🎉\n Иди гуляй)"
    await message.reply(Lessons, parse_mode='HTML', disable_web_page_preview=True)

@dp.message_handler(commands=['tomorow','Пары на завтра'])
async def scheduler_today(message: types.Message):
    Lessons = "<b> Пары на " + str(time_lesson.TodayToEmoji(1)) + str(time_lesson.NumberOfMonth()) + " неделя. </b> \n" 
    group = UsersDB.find_one({"chat_id":message.chat.id})["group"]
    check_lesson = False # Проверяет, есть ли вообще пары на сегодня
    for i in range(1,7):
        if time_lesson.NumberOfMonth() % 2 == 0: 
            a = i*2 + 12
        else:
            a = (i*2)-1 + 12
        if Scheduler.get_lesson(time_lesson.todayIs()+a,group) == "nan":
            pass
        else: 
            check_lesson = True
            # Четная/ не четная неделя
            Lessons = Scheduler.ready_lesson(Lessons,group, a,i)
    if check_lesson is False:
        Lessons = "<b>Завтра нету пар </b> ✨🎉\n Можешь спать и гулять))"
    await message.reply(Lessons, parse_mode='HTML', disable_web_page_preview=True)


# Уведомлялки утром
async def notif_morning():
    for user in UsersDB.find({"sub":"True"}):
        #try:
        group = UsersDB.find_one({"chat_id":user["chat_id"]})["group"]
        Lesson = "<b> Доброе утро! </b> \n "
        a = 0 #Локальная переменная - формирует адрес исходя из четной/нечетной неделе и когда.
        if Scheduler.get_lesson(time_lesson.todayIs()+1,group) == "nan":
            Lesson = Lesson + " <code> Ты везунчик, можешь немного поспать, к первой не надо. </code> \n"
            if Scheduler.get_lesson(time_lesson.todayIs()+2,group) == "nan":
                Lesson = Lesson + "Ко второй тоже. Вообще топ.\n"
        Lesson = Lesson + "Сегодня у тебя: \n"
        check_lesson = False
        for i in range(1,7):
            if time_lesson.NumberOfMonth() % 2 == 0: 
                 a = i*2
            else:
                a = (i*2)-1
             # Четная/ не четная неделя
            if Scheduler.get_lesson(time_lesson.todayIs()+a,group) == "nan":
                pass
            else: 
                check_lesson = True
                Lesson = Scheduler.ready_lesson(Lesson,group,a,i)
        if check_lesson is False:
            Lesson = "<b>Сегодня нету пар </b> ✨🎉\n Спи спокойно и иди гуляй)"       
        await bot.send_message(user["chat_id"], Lesson, parse_mode='HTML', disable_web_page_preview=True)


    
    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    scheduler = BackgroundScheduler()
    scheduler.add_job(notif_morning, 'cron', id='notif_morning', replace_existing=True, hour=8, minute = 40)
    scheduler.start()