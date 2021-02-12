
import os,sys,time
from aiogram.dispatcher.filters import state
import aiohttp
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from pymongo import MongoClient
import utils.scheduler as Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

import config

API_TOKEN = config.Auth.API_TOKEN


# Логи
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=API_TOKEN)
#storage = MongoStorage(host=config.MongoAuth.host, port=27017, db_name='users', username="admin", password=config.MongoAuth.password) #Не работает с библиотекой
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
#Инициализируем базу данных(Mongo проста и бесплатная)
client = MongoClient('mongodb+srv://admin:' + str(config.Auth.password_db) + "@cluster0.cy3ca.mongodb.net/", 27017)
db = client['Data']
UsersDB = db["Users"]
GroupDB = db["Group"]

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
        await message.reply("<b> Привет, рад тебя видеть снова </b>", parse_mode='HTML', disable_web_page_preview=True)
        await Group.complete.set()
    
# Внесение группы  
@dp.message_handler(state=Group.group_select)
async def select_group(message: types.Message):
    if Check_Group(message.text) is True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Да", "Нет")
        with open(config.FileLocation.cmd_group,'r', encoding='utf-8') as file:
            await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)
        await Group.next()
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
    await Group.next()
    menu(message)
    # Конец регистрации

dp.message_handler(state=Group.complete)
async def menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Что у меня сегодня", "На этой неделе", "Мои задачи", "Настройки")
    with open(config.FileLocation.cmd_menu,'r', encoding='utf-8') as file:
            await message.reply(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)