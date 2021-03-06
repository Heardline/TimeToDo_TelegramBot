from pymongo import MongoClient
import re
def Comlete_task(chat_id,text,db):
    db['task'].find_one_and_update({"chat_id":chat_id, "name": re.split(r' по предмету:',text)[0]}, {"$set": {"status":"complete"}})
    print(re.split(r'по предмету:',text)[0] + " и " + re.split(r'по предмету:',text)[1])
class Task():
    def __init__(self,name,timetodo,lesson,chat_id):
        self.name = name
        self.timetodo = timetodo
        self.lesson = lesson
        self.chat_id = chat_id
    def addtodb(self,db):
        db.insert_one({"chat_id":self.chat_id, "name": self.name, "lesson":self.lesson,"timetodo":self.timetodo, "status":"begin"})
