from logging import ERROR
import logging
from sys import intern
import pandas as pd,os
import enum
from sqlalchemy.sql.expression import column
from sqlalchemy import select,insert
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.traversals import CACHE_IN_PLACE
import utils.time_lessons as time_lesson
from sqlalchemy import Column, Integer, BigInteger,String,Boolean, DateTime
import utils.scrap_schedul as updater
from utils.db.base import Base
class Student(Base):
    __tablename__ = "student"
    __table_args__ = {'extend_existing': True}
    telegram_id = Column('telegram_id',BigInteger,primary_key=True)
    grp = Column('grp',String)
    notify = Column('notify',Boolean)
class Lesson(Base):
    __tablename__ = "lesson"
    __table_args__ = {'extend_existing': True}
    id = Column('id',Integer, primary_key=True)
    name = Column('name', String)
    teacher = Column('teacher',String)
    type = Column('type',String)
    room = Column('room',String)
    grp = Column('grp',String)
    day = Column('day',Integer)
    week = Column('week',Integer)
    time = Column('time',Integer)
class Task(Base):
    __tablename__ = "task"
    __table_args__ = {'extend_existing': True}
    id = Column('id',Integer,primary_key=True)
    name = Column('name',String)
    desc = Column('desc',String)
    student = Column('student', ForeignKey('student.telegram_id'))
    lesson = Column('lesson',ForeignKey('lesson.id'))
    time = Column('day',DateTime)
class Group(Base):
    __tablename__ = "group"
    __table_args__ = {'extend_existing': True}
    id = Column('id',Integer,primary_key=True)
    name = Column('name',String)
    univer = Column('univer',String)

def setup_notify(boolen,telegram_id):
    try:
        cursor.execute(f"Update students set notify = {boolen} WHERE telegram_id = '{telegram_id}';")
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL setup_notify", error)

def check_group(group):
    cursor.execute("SELECT id FROM groups WHERE name = '" + group + "';")
    if cursor.fetchone():
        print(cursor.fetchone())
        return True
    else:
        return False
        

def check_user(telegram_id):
    cursor.execute(f"SELECT grp FROM students WHERE telegram_id = '{telegram_id}';")
    if cursor.fetchone():
        print(cursor.fetchone())
        return True
    else:
        return False
    
def update_data():
    updater.download_xlsx()
    remove_data()
    import_from_xlsx()

async def import_group(message,group,univercity):

    db_session = message.bot.get('db')
    async with db_session() as session:
        group = Group(name=group,univer=univercity)
        session.add(group)
        await session.commit()
        print(group)




def add_user(group,telegram_id):
    try:
        execute_com = f"INSERT INTO students (grp,telegram_id, notify) VALUES ('{group}','{telegram_id}', True);"
        cursor.execute(execute_com)
        connection.commit()
        print(f"Пользователь {telegram_id} успешно зарегестирован в PostgreSQL")
        return True
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL add_user", error)
        return False

def get_group(telegram_id):
    try:
        execute_com = f"SELECT grp FROM students WHERE telegram_id = '{telegram_id}';"
        cursor.execute(execute_com)
        connection.commit()
        return cursor.fetchone()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL get_group", error)
        return False

def init_db():
    try:
        cursor = connection.cursor()
        execute_com = ''''''
        cursor.execute(execute_com)
        connection.commit()
        print("Таблица успешно создана в PostgreSQL")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

async def import_lesson(message,name,teacher,room,type,time, group):
    if room != room:
        room = ''
    if teacher != teacher:
        teacher = ''
    if type != type:
        type = ''
    if time%2 == 1:
        odd = 0
    else:
        odd = 1
    db_session = message.bot.get('db')
    async with db_session() as session:
        lesson = Lesson(name=str(name),type=str(type),room=str(room),grp=group,teacher=str(teacher),day=time//12,week=odd,time=time%12)
        session.add(lesson)
        await session.commit()

def remove_data():
    try:
        cursor = connection.cursor()
        execute_com = '''DELETE from lessons;'''
        cursor.execute(execute_com)
        #print(name,teacher,room,type,time%12," ", time//12, " ",odd)
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL remove_data ", error)

async def import_from_xlsx(message):
    excel_names = os.listdir("data/xlsx/")
    await message.answer('Запускаю процесс обновления данных...')
    for names in excel_names:
        data_df = pd.read_excel("data/xlsx/"+names,header=1)
        for index in data_df.columns:
            if "-" in str(index):
                await import_group(message,str(index),names.split(r'_')[0])
                for time in range(1,75):
                    if str(data_df.iloc[time,data_df.columns.get_loc(index)]) == "nan":
                        pass
                    else:
                        await import_lesson(message,data_df.iloc[time,data_df.columns.get_loc(index)],data_df.iloc[time,data_df.columns.get_loc(index)+2],data_df.iloc[time,data_df.columns.get_loc(index)+3],data_df.iloc[time,data_df.columns.get_loc(index)+1],time,index) 
    await message.answer("Обновление данных завершено.")
        #print(data_df.iloc[2,data_df.columns.get_loc("ГДБО-01-20")])


#Получение данных из dataframe. time_row - код времени(в зависимости от четной и не четной недели)
def get_lesson(time_row,group):
    try:
        cursor = connection.cursor()
        execute_com = f"SELECT * FROM lessons WHERE grp = {group} and tstart = {time_row%12} and day = {time_row//12};"
        cursor.execute(execute_com)
        #print(name,teacher,room,type,time%12," ", time//12, " ",odd)
        return cursor.fetchone()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL get_lesson", error)

