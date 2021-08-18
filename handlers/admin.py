
from aiogram import types
from config import Settings

from utils.db.db import import_from_xlsx

async def isAdmin(message: types.Message):
    if message.from_user.id in Settings.admin:
        return True
    else:
        return False

# async def restart(message: types.Message):
#     if isAdmin(message):

# async def broadcast(message: types.Message):
#     if isAdmin(message):

async def update_data(message: types.Message):
    if isAdmin(message):
        await import_from_xlsx(message)

# async def statistics(message: types.Message):
#     if isAdmin(message):