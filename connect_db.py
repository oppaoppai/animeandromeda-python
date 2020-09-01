from pymongo import MongoClient

CONNECTION = "xxxx"


def connect():
    return MongoClient(
        CONNECTION,
        connect=False
    )
