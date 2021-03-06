from pymongo import MongoClient
import re

def Comlete_task(chat_id,text,db):
    db['task'].find_one_and_update({"chat_id":chat_id, "name": re.split(r" @ ",text)[0]}, {"$set": {"status":"complete"}})
def Change_task(chat_id,text,db,name):
    pass
class Task():
    def __init__(self,name,timetodo,lesson,chat_id):
        self.name = name
        self.timetodo = timetodo
        self.lesson = lesson
        self.chat_id = chat_id
    def addtodb(self,db):
        db.insert_one({"chat_id":self.chat_id, "name": self.name, "lesson":self.lesson,"timetodo":self.timetodo, "status":"begin"})
