from sqlalchemy import and_, select
from utils.db.db import Lesson, Student
import utils.time_lessons as time_lesson

# Поиск студента 
async def get_student(db_session, user_id: int) -> Student:
    sql = select(Student).where(Student.telegram_id == user_id)
    request = await db_session.execute(sql)
    student: Student = request.scalar()
    return student

# Поиска студентов с включенными уведомлениями
async def get_students(bot):
    db_session = bot.get('db')
    async with db_session() as session:
        sql = select(Student).where(Student.notify == True)
        request = await session.execute(sql)
        return request.scalars()

# Передает семинар для оповещения
async def get_next_lesson(bot,telegram_id):
    db_session = bot.get('db')
    async with db_session() as session:
        student = await get_students(session,telegram_id)
        group = student.grp
        if time_lesson.NumberOfMonth() % 2 == 0: week=0 
        else: week=1 
        sql = select(Lesson).where(and_(Lesson.grp == group, time_lesson.todayIs(), Lesson.week == week, Lesson.time == time_lesson.convertHourtoLesson))
        request = await session.execute(sql)
        return request.scalar()