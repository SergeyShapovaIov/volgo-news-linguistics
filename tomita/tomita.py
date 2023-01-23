from pymongo import MongoClient
import subprocess
import re
import os
import sys
import pymongo
from bson.objectid import ObjectId


def checkPersons(db):
    if not os.path.isfile('personFIO.txt'):
        f = open('personFIO.txt', 'w')
        person = db.person.find()
        for text in person:
            f.write(text.get("personName") + '\n')
        f.close()


def checkPlaces(db):
    if not os.path.isfile('attractionsNames.txt'):
        f = open('attractionsNames.txt', 'w')
        attractions = db.attractions.find()
        for text in attractions:
            f.write(text.get("attractionsNames") + '\n')
        f.close()


def findFact(id=None):
    client = pymongo.MongoClient(
        "mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
    db = client.test
    coll = db['news']
    os.chdir("../tomita")
    checkPersons(coll)
    checkPlaces(coll)

    if id is None:
        textForAnalysis = coll.find({"forAnalysis": True})
    else:
        textForAnalysis = coll.find({"_id": ObjectId(id)})

    if textForAnalysis.count(True) > 0:

        i = 0
        for fact in textForAnalysis:

            print(i)
            i = 1 + i
            f = open('input.txt', 'w')
            f.write(fact.get("newsText"))
            f.close()
            p = subprocess.Popen(["tomita-parser", "config.proto"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            out = out.decode("utf-8", "strict")
            result = re.findall(
                r'(Person|Attractions)[\n\s{]*(FIO[\s=а-яёА-яa-zA-Z0-9]+|Name[\s=а-яА-яёa-zA-Z0-9]+)(Text[\s=а-яА-яёa-z0-9№A-Z,!.?\"\-—–]+)',
                out)

            coll.update_one({"_id": fact.get("_id")}, {"$set": {"forAnalysis": False}})

            if not result:
                continue
            db['analysis'].insert_one({'_id': fact.get('_id'), 'forTonality': True})
            res = []
            for f in result:
                c = f[2][7:-2]
                print(c)
                db.analysis.update_one({'_id': fact.get('_id')}, {"$push": {'newsWithMention': c}})

    else:
        print('Нету новый новостей на анализ')



