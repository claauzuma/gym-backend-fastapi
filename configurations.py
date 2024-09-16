from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://claauzuma:940250311@cluster0.7jf4lsj.mongodb.net/gymdatabase?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
database = client.gymdatabase

alumnos_collection = database["alumnos_data"]
clases_collection = database["clases_data"]
rutinas_collection = database["rutinas_data"]
profesores_collection = database["profes_data"]
admins_collection = database["admins_data"]
