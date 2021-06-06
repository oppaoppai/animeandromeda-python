import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

CONNECTION = os.environ.get("DB_AUTH")


def connect():
    return MongoClient(CONNECTION, connect=False)
