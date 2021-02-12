import os,sys,datetime,time


def NumberOfMonth():
    return datetime.datetime.today().isocalendar()[1] - datetime.datetime.today().replace(day=1).isocalendar()[1] + 1 
def todayIs():
    today = datetime.datetime.today().weekday()
    return today*12
