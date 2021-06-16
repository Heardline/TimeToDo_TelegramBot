import config
from aiogram import types, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageNotModified
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

@dp.callback_query_handler(text_contains="complete")
async def finish_task(call: CallbackQuery):
    await call.answer("Готово",cache_time=60)
    task_manager.Comlete_task(call.from_user.id, call.message.text, db)
    await bot.delete_message(call.from_user.id, call.message.message_id)

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(finish_task, text_contains="complete")
