
from sqlalchemy import select, and_

from utils.db.db import Lesson
from aiogram import types
from commands import get_student
import utils.time_lessons as time_lesson

# Пары на сегодня

async def scheduler_today(message: types.Message):
    Lesson_text = f"<b> {time_lesson.TodayToEmoji(0)} | {time_lesson.NumberOfMonth()} неделя. </b> \n"
    db_session = message.bot.get('db')
    async with db_session() as session:
        # Четная/ не четная неделя
        if time_lesson.NumberOfMonth() % 2 == 0:
            week = 0
        else:
            week = 1
        student = await get_student(session, message.from_user.id)
        group = student.grp
        sql = select(Lesson).where(and_(Lesson.grp == group,
                                        Lesson.day == time_lesson.todayIs(), Lesson.week == week))
        request = await session.execute(sql)
        lessons = request.scalars()
        k = 0
        for lesson in lessons:
            Lesson_text += (f"{time_lesson.NumberToEmoji(lesson.time//2)}\n {lesson.name} |  {lesson.type} | {lesson.room} \n {lesson.teacher} \n")
            k += 1
        if k == 0:
            Lesson_text = "<b>Сегодня нету пар </b> ✨🎉\n"
    await message.answer(Lesson_text, parse_mode='HTML', disable_web_page_preview=True)

# Пары на завтра

async def scheduler_tomorrow(message: types.Message):
    Lesson_text = f"<b> {time_lesson.TodayToEmoji(1)} | {time_lesson.NumberOfMonth()} неделя. </b>\n"
    db_session = message.bot.get('db')
    async with db_session() as session:
        # Четная/ не четная неделя
        if time_lesson.NumberOfMonth() % 2 == 0:
            week = 0
        else:
            week = 1
        student = await get_student(session, message.from_user.id)
        group = student.grp
        sql = select(Lesson).where(and_(Lesson.grp == group, Lesson.day == (
            time_lesson.todayIs()+1) % 7, Lesson.week == week))
        request = await session.execute(sql)
        lessons = request.scalars()
        k = 0
        for lesson in lessons:
            Lesson_text += (f"{time_lesson.NumberToEmoji(lesson.time // 2)}\n {lesson.name} |  {lesson.type} | {lesson.room} \n {lesson.teacher} \n")
            k += 1
        if k == 0:
            Lesson_text = "<b>Завтра нету пар </b> ✨🎉\n)"
    await message.answer(Lesson_text, parse_mode='HTML', disable_web_page_preview=True)

# Пары на эту неделю

async def scheduler_week(message: types.Message):
    Lesson_text = f" <b>👨‍🏫 Расписание на {time_lesson.NumberOfMonth()} неделю. </b>\n \n"
    db_session = message.bot.get('db')
    async with db_session() as session:
        # Четная/ не четная неделя
        if time_lesson.NumberOfMonth() % 2 == 0:
            week = 0
        else:
            week = 1
        student = await get_student(session, message.from_user.id)
        group = student.grp
        for day in range(1, 7):
            Lesson_text += f"<b> {time_lesson.TodayToEmoji(day)} \n</b> "
            sql = select(Lesson).where(and_(Lesson.grp == group, Lesson.day == (
                time_lesson.todayIs()+day) % 7, Lesson.week == week))
            request = await session.execute(sql)
            lessons = request.scalars()
            k = 0
            for lesson in lessons:
                Lesson_text += (f"{time_lesson.NumberToEmoji((lesson.time+1) // 2)}\n{lesson.name} |  {lesson.type} | {lesson.room} {lesson.teacher} \n")
                k += 1
            if k == 0:
                Lesson_text += f"<b>Нету пар </b> ✨\n"
            Lesson_text += '\n'
    await message.answer(Lesson_text, parse_mode='HTML', disable_web_page_preview=True)
