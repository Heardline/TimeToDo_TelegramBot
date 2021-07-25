from datetime import datetime
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
    lesson = Column('lesson',String)
    time = Column('day',DateTime)
class Group(Base):
    __tablename__ = "group"
    __table_args__ = {'extend_existing': True}
    id = Column('id',Integer,primary_key=True)
    name = Column('name',String)
    univer = Column('univer',String)

 
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
