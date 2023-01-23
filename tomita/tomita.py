from pymongo import MongoClient
import subprocess
import re
import os
import sys
import pymongo
from bson.objectid import ObjectId

import os
import time
from pymongo import MongoClient
from progress.bar import IncrementalBar


def tomita():
    # Строка подключения к базе данных
    CONNECTION_STRING = "mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority"
    # Подключение к нужной коллекции
    client = MongoClient(CONNECTION_STRING)
    db = client.test
    collection = db.news
    collection_list = list(collection.find({}))

    sentence_coll = db.sentence
    clear = lambda: os.system('clear')
    # Инициализация прогресс бара
    bar = IncrementalBar('Countdown', max=len(collection_list))
    for news in collection_list:
        # Запуск парсера, если он не был задействован на данную запись
        if "tomita" not in news:
            clear()
            bar.next()
            time.sleep(0.1)
            print('\n')
            # Запись текста новостей во входной файл парсера
            with open("../input.txt", "w") as file:
                file.write(news['newsText'])

            os.system("./tomita/tomita-parser ../config.proto")

            # Откытие файла выходных данных для чтения
            with open("../output.txt") as file:
                file_output = file.read()
                strings = file_output.split('\n')
                # Формирование выборки нужных данных по строкам
                for i in range(len(strings)):
                    if "Politician" in strings[i]:
                        words = strings[i].split("Politician =")
                        if words[1].find('_'):
                            words = words[1].strip().replace("_", " ")
                        # Запись предложения, в котором нашлась нужная личность
                        sentence = strings[i - 3]
                        # Добавление данных в коллекцию
                        sentence_coll.insert_one({'fact': words, 'sentence': sentence})
                    elif "Attraction" in strings[i]:
                        words = strings[i].split("Attraction =")
                        if words[1].find('_'):
                            words = words[1].strip().replace("_", " ")
                        # Запись предложения, в котором нашлось нужное сооружение
                        sentence = strings[i - 3]
                        # Добавление данных в коллекцию
                        sentence_coll.insert_one({'fact': words, 'sentence': sentence})
    bar.finish()


def main():
    try:
        tomita()
    except Exception as exception:
        print(f"Ошибка {exception}")


if __name__ == "__main__":
    main()


# def checkPersons(db):
#     if not os.path.isfile('personFIO.txt'):
#         f = open ('personFIO.txt', 'w')
#         person = db.person.find()
#         for text in person:
#             f.write(text.get("personName") +'\n')
#         f.close()
#
#
# def checkPlaces(db):
#     if not os.path.isfile('attractionsNames.txt'):
#         f = open ('attractionsNames.txt', 'w')
#         attractions = db.attractions.find()
#         for text in attractions:
#             f.write(text.get("attractionsNames") +'\n')
#         f.close()
#
#
# def findFact(id = None ):
#     client = pymongo.MongoClient(
#         "mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
#     db = client.test
#     coll = db['news']
#     os.chdir("../tomita")
#     checkPersons(db)
#     checkPlaces(db)
#
#     if id is None:
#         textForAnalysis = db.data.find({"forAnalysis": True})
#     else:
#         textForAnalysis = db.data.find({"_id": ObjectId(id)})
#
#     if textForAnalysis.count(True) > 0:
#
#         i = 0
#         for fact in textForAnalysis:
#
#             print(i)
#             i = 1+i
#             f = open('input.txt', 'w')
#             f.write(fact.get("newsText"))
#             f.close()
#             p = subprocess.Popen(["tomita-parser", "config.proto"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             out, err = p.communicate()
#             out = out.decode("utf-8", "strict")
#             result = re.findall(r'(Person|Attractions)[\n\s{]*(FIO[\s=а-яёА-яa-zA-Z0-9]+|Name[\s=а-яА-яёa-zA-Z0-9]+)(Text[\s=а-яА-яёa-z0-9№A-Z,!.?\"\-—–]+)',out )
#
#             db.data.update_one({"_id": fact.get("_id")},{"$set":{"forAnalysis": False}})
#
#             if not result:
#                 continue
#             db.analysis.insert_one({'_id': fact.get('_id'), 'forTonality': True})
#             res = []
#             for f in result:
#                 c = f[2][7:-2]
#                 print(c)
#                 db.analysis.update_one({'_id': fact.get('_id')},{"$push": {'newsWithMention': c} })
#
#     else:
#         print('Нету новый новостей на анализ')
#
#
#


