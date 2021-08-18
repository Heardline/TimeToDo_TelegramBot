from config import Settings
from aiogram import types

# Главное меню
async def menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Сегодня ⏲", "Завтра 📆", "Неделя 📅","Мои задачи 📋","Настройки 🛠")
    with open(Settings.cmd_menu,'r', encoding='utf-8') as file:
            await message.answer(file.read(), parse_mode='HTML', disable_web_page_preview=True, reply_markup=markup)