import pandas
import utils.time_lessons as time_lesson
def get_pandas(univ):
    return pandas.read_excel("data/xlsx/ИНТЕГУ_17-20.xlsx", sheet_name='Sheet1')
lessons = [("","","")]
data = get_pandas("ИНТЕГУ")
#print(data["ГИБО-05-19"].index)
#print(data.at[5+2,"ГИБО-05-19"])
#print(data.columns[data.columns.get_loc("ГИБО-05-19")+1])
#print(data.at[5+2, data.columns.get_loc("ГИБО-05-19")])
#print(data.iloc[4][data.columns.get_loc("ГИБО-05-19")])
#print(data.iloc[4][data.columns.get_loc("ГИБО-05-19")+1])

#Получение данных из dataframe. time_row - код времени(в зависимости от четной и не четной недели)
def get_lesson(time_row,group):
    return str(data.iloc[time_row][data.columns.get_loc(group)])

def get_lesson_type(time_row,group):
    return str(data.iloc[time_row][data.columns.get_loc(group)+1])
def get_lesson_teacher(time_row,group):
    return str(data.iloc[time_row][data.columns.get_loc(group)+2])
def get_lesson_cabinet(time_row,group):
    return str(data.iloc[time_row][data.columns.get_loc(group)+3])

def ready_lesson(Lessons,group,number,time_row):
    # Время + название + тип + кабинет + преподаватель
    lesson = Lessons + time_lesson.NumberToEmoji(time_row) + "\n" + get_lesson(time_lesson.todayIs()+number,group) + " | " + get_lesson_type(time_lesson.todayIs()+number,group)  +  " | "  + get_lesson_cabinet(time_lesson.todayIs()+number,group) + " \n " + get_lesson_teacher(time_lesson.todayIs()+number,group) + "\n"
    return lesson
    