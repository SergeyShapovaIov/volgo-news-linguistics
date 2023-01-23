from w2v import create_w2v_model
from dbtext import newsToText
import pymongo

client = pymongo.MongoClient("mongodb+srv://mongo-root:passw0rd@cluster0.qkh3grh.mongodb.net/?retryWrites=true&w=majority")
db = client.test
coll = db['news']

newsToText(coll)
create_w2v_model()
