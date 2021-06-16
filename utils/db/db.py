import pandas as pd,os
import utils.time_lessons as time_lesson

import utils.scrap_schedul as updater


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

def import_group(group,univercity):
    try:
        execute_com = '''INSERT INTO groups ( name, univercity) VALUES (%s, %s);'''
        cursor.execute(execute_com,(group,univercity))
        connection.commit()
        return True

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        return False


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

def import_lesson(name,teacher,room,type,time, group):
    try:
        cursor = connection.cursor()
        execute_com = '''INSERT INTO lessons (subj, prep,room,type,tstart,day,odd,grp) VALUES (%s, %s,%s,%s,%s,%s,%s,%s);'''
        if (time %2) == 1:
            odd = 0
        else: odd = 1
        cursor.execute(execute_com,(str(name),str(teacher),str(room),str(type),time%12, time//12,odd, str(group)))
        #print(name,teacher,room,type,time%12," ", time//12, " ",odd)
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL import_lesson", error, name, teacher,room)

def remove_data():
    try:
        cursor = connection.cursor()
        execute_com = '''DELETE from lessons;'''
        cursor.execute(execute_com)
        #print(name,teacher,room,type,time%12," ", time//12, " ",odd)
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL remove_data ", error)

def import_from_xlsx():
    excel_names = os.listdir("data/xlsx/")
    for names in excel_names:
        data_df = pd.read_excel("data/xlsx/"+names,header=1)
        for index in data_df.columns:
            if "-" in str(index):
                import_group(str(index),names.split(r'_')[0])
                for time in range(1,75):
                    if str(data_df.iloc[time,data_df.columns.get_loc(index)]) == "nan":
                        pass
                    else:
                        import_lesson(data_df.iloc[time,data_df.columns.get_loc(index)],data_df.iloc[time,data_df.columns.get_loc(index)+2],data_df.iloc[time,data_df.columns.get_loc(index)+3],data_df.iloc[time,data_df.columns.get_loc(index)+1],time,index) 
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
