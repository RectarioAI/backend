from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

# from models.user_model import User


load_dotenv()

user = quote_plus(getenv("USER"))
password = quote_plus(getenv("PASSWORD"))
database = quote_plus(getenv("DATABASE"))


# Connect to the database
def connect() -> MongoClient:
    connetion = MongoClient(f"mongodb+srv://{user}:{password}@cluster0.htedn.mongodb.net/?retryWrites=true&w=majority")
    return connetion

connection = connect()
currentDb = connection["RectarIA"]

# Get the collection
def get_collection(collectionName: str, db = currentDb):
    collection = db[collectionName]
    return collection

