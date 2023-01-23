
PATH = 'model/kurs_model/'

from dbtext import newsToText
from pyspark.sql import SparkSession
from pyspark.ml.feature import Word2VecModel
from pprint import pprint
import pymongo
import os

client = pymongo.MongoClient("mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
db = client.test
coll = db['news']

if (not os.path.exists('model')):
    if (not os.path.exists('data_text')):
        print("Папка создана")
        os.mkdir('data_text')
    newsToText(db['news'])
test_words = ["алимов","бочаров"]

spark = SparkSession \
    .builder \
    .appName("SimpleApplication") \
    .getOrCreate()

model = Word2VecModel.load(PATH)

pprint("Контекстные синонимы слов, полученные из модели, обученной на статьях:")

for test_word in test_words:
    pprint("-"*20)
    pprint(test_word)
    result = model.findSynonyms(test_word, 5).collect()
    for el in result:
        pprint(el)

spark.stop()