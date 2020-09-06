from flask import Flask, Response, request
from flask_gzip import Gzip
from flask_cors import CORS
from connect_db import connect
from helpers import compareJSONdate, convertEpisode
from bson.json_util import dumps as json
from json import dumps

app = Flask(__name__)

BASE_URL = "/api/v2/anime/"

client = connect()
db = client["andromeda"]
collection = db["animes"]
report_collection = db["reports"]

cors = CORS(app)
gzip = Gzip(app)


@app.route("/")
def index():
    return "animeandromeda API"


@app.route(BASE_URL + "get/<id>")
def getAnime(id):
    query = collection.find(
        {"$or": [
            {"series_pretty": id},
            {"series": id},
            {"title": id},
        ]})

    query = sorted(query, key=lambda x: convertEpisode(x["ep"]))

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "search/")
@app.route(BASE_URL + "search/<id>")
def searchAnime(id=""):
    if id == "":
        return Response(response=dumps([]), status=200, mimetype="application/json")

    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "redundant": {"$first": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "title": {"$first": "$title"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "count": {"$sum": 1},
            },
        },
        {
            "$match": {
                "$or": [
                    {"pretty": {"$regex": id, "$options": "i"}},
                    {"title": {"$regex": id, "$options": "i"}},
                    {"redundant": {"$regex": id, "$options": "i"}},
                ],
            }
        }])

    query = sorted(query, key=lambda x: x["redundant"])

    if len(query) > 0:
        data = json(query)
        return Response(response=data, status=200, mimetype="application/json")
    return {}


@app.route(BASE_URL + "latest")
def getLatestAnimes():
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "updated": {"$first": "$updated"},
                "aired": {"$first": "$aired"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "count": {"$sum": 1},
            }
        }
    ])

    query = sorted(query, key=lambda x: compareJSONdate(x["updated"]), reverse=True)

    data = json(query[:12])
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "latest/aired")
def getLastAiredAnimes():
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "updated": {"$first": "$updated"},
                "airedFirst": {"$first": "$airedFirst"},
                "airedLast": {"$first": "$airedLast"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "count": {"$sum": 1},
            }
        }
    ])

    query = sorted(query, key=lambda x: compareJSONdate(x["airedLast"]), reverse=True)

    data = json(query[:16])
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "latest/airing")
def getAiringAnimes():
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "updated": {"$first": "$updated"},
                "airing": {"$first": "$airing"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "count": {"$sum": 1},
            }
        },
        {"$match": {"airing": {"$eq": True}}}
    ])

    query = sorted(query, key=lambda x: x["pretty"])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "random")
def getRandomAnimes():
    query = collection.aggregate([
        {
            "$sample": {
                "size": 6
            },
        }
    ])

    query = map(lambda x:  {
        "_id": x["_id"],
        "series": x["series"],  # presente per forza
        "series_pretty": x["series_pretty"] if "series_pretty" in x else None,  # cambierò
        "title": x["title"] if "title" in x else None,
        "pic": x["pic"] if "pic" in x else None,
        "idMAL": x["idMAL"] if "idMAL" in x else None,
    }, query)

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "report", methods=["POST"])
def report():
    data = request.get_json(silent=True)
    report_dict = {"series": data["series"], "episode": data["episode"]}
    report_collection.insert_one(report_dict)
    return {"insert": "success"}
