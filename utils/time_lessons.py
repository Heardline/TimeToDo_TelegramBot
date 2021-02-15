import os,sys,datetime,time
emojiNumber = {
    1:"1️⃣ <b>9:00 - 10:30</b>",
    2:"2️⃣ <b>10:40 - 12:40</b>",
    3:"3️⃣ <b>12:40 - 14:10</b>",
    4:"4️⃣ <b>14:20 - 15:50</b>", 
    5:"5️⃣ <b>16:20 - 17:50</b>",
    6:"6️⃣ <b>18:00 - 19:30</b>",
}
emojiToday = {
    1:"👨‍🎓Понедельник👩‍🎓",
    2:"👨‍🏫Вторник👩‍🏫",
    3:"👩‍💻Среда👨‍🏫",
    4:"👷‍♀️Четверг👷‍♂️",
    5:"👩‍🎨Пятница👨‍🎨",
    6:"😑Суббота🍻",
    7:"✨Воскресенье",
}


def NumberOfMonth():
    return datetime.datetime.today().isocalendar()[1] - datetime.datetime.today().replace(day=1).isocalendar()[1] + 1 
def todayIs():
    today = 1
    #today = datetime.datetime.today().weekday()
    return today*12
def NumberToEmoji(number):
    return emojiNumber[int(number)]
def TodayToEmoji():
    return emojiToday[datetime.datetime.today().weekday()+1]