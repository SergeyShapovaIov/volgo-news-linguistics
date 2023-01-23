from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from pymongo import MongoClient
import pymongo
import re

def main():
    client = pymongo.MongoClient(
        "mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
    db = client.test
    coll = db['analyses']
    result = coll.find({u'forTonality': True})
    mas = []
    # добавление к analysis поля 'forTonality' чтобы одно и то же не считывать
    # for res in result:
    #     data.update({u'_id': res['_id']}, { u'$set': { 'forTonality': True } }, **{ 'upsert': True })

    def getTonality(messages):
        tokenizer = RegexTokenizer()
        model = FastTextSocialNetworkModel(tokenizer=tokenizer)
        results = model.predict(messages, k=1)
        regex = r"[\w]+\(\['([\w]+)'\]\)"
        mas.clear()
        # результат
        for message, sentiment in zip(messages, results):
            match = re.search(regex, str(sentiment.keys()))
            mas.append(match.group(1))
        return mas

    for arrays in result:
        id = arrays['_id']
        messages = arrays['newsWithMention']
        result = getTonality(messages)
        db['tonality'].update({u'_id': id, u'tonality': result}, { u'$setOnInsert': { u'_id': id, u'tonality': result} }, **{ 'upsert': True })
        coll.update({u'_id': id}, { u'$set': { u'forTonality': False} }, **{ 'upsert': True })
    
    print('Провека тональносьт завершена')