import pymongo as pm
from bson import ObjectedID
from datetime import datetime

# #PyQt5ㅇㅔㅅㅓ Matplotlib ㄱㅡㄹㅣㄱㅣ
# #https://codetorial.net/articles/matplotlib_in_pyqt5.html

#matplotlib 데이터 시각화
#https://zzsza.github.io/development/2018/08/24/data-visualization-in-python/


connection = pm.MongoClient("mongodb://localhost:27017/")
db = connection.get_database("DB")
collection = db.get_collection("Collection")

curr = datetime.now()

if(curr.hour == 23 and curr.minute == 59 ):
    import induceGUI as gui
    collection.insert_one({
        "date" : curr.date(),
        "recognition_time" : gui.rcg.alert.total_time,
        "blink_count" : gui.rcg.alert.total_blink
    })
    gui.rcg.alert.total_time = 0
    gui.rcg.alert.total_blink = 0
