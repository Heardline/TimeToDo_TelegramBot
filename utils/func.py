from sqlalchemy import and_, select
from utils.db.db import Lesson, Student
import utils.time_lessons as time_lesson

# Получение сессии базы данных
def get_db_session(bot):
    return bot.get('db')

# Поиск студента по ID пользователя в Telegram
async def get_student(db_session, user_id: int) -> Student:
    sql = select(Student).where(Student.telegram_id == user_id)
    request = await db_session.execute(sql)
    student: Student = request.scalar_one_or_none()
    return student

# Поиск студентов, у которых включены уведомления
async def get_students_with_notifications(bot):
    db_session = get_db_session(bot)
    async with db_session() as session:
        sql = select(Student).where(Student.notify == True)
        request = await session.execute(sql)
        return request.scalars().all()

# Получение следующего урока студента
async def get_next_lesson(bot, telegram_id):
    db_session = get_db_session(bot)
    async with db_session() as session:
        student = await get_student(session, telegram_id)
        if not student:
            return None

        group = student.grp
        week = 0 if time_lesson.NumberOfMonth() % 2 == 0 else 1
        sql = select(Lesson).where(and_(
            Lesson.grp == group,
            time_lesson.todayIs(),
            Lesson.week == week,
            Lesson.time == time_lesson.convertHourtoLesson
        ))
        request = await session.execute(sql)
        return request.scalar_one_or_none()
