from flask import Flask, Response, request
from flask_cors import CORS
from flask_compress import Compress
from flaskr.db.connect_db import connect
from flaskr.utils.helpers import compareJSONdate, convertEpisode, convertJST
from bson.json_util import dumps as json
from json import dumps

app = Flask(__name__)
app.config["COMPRESS_ALGORITHM"] = "br"

BASE_URL = "/api/v2/anime/"

client = connect()
db = client["andromeda"]
collection = db["animes"]
report_collection = db["reports"]

CORS(app)
Compress(app)


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


@app.route(BASE_URL + "genre/<genres>")
def getAnimeByGenres(genres):
    genres_list = []
    if "," in genres:
        genres_list = genres.split(",")
    else:
        genres_list.append(genres)

    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "title": {"$first": "$title"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "genres": {"$first": "$genres"},
                "count": {"$sum": 1},
            },
        },
        {
            "$match": {"genres": {"$all": genres_list}}
        }])

    query = sorted(query, key=lambda x: x["pretty"])

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
                "title_romaji": {"$first": "$title_romaji"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "premiere": {"$first": "$premiere"},
                "count": {"$sum": 1},
            },
        },
        {
            "$match": {
                "$or": [
                    {"pretty": {"$regex": id, "$options": "i"}},
                    {"title": {"$regex": id, "$options": "i"}},
                    {"title_romaji": {"$regex": id, "$options": "i"}},
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
                "premiere": {"$first": "$premiere"},
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
    size = request.args.get('size')
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "series": {"$first": "$series"},
                "series_pretty": {"$first": "$series_pretty"},
                "title": {"$first": "$title"},
                "pic": {"$first": "$pic"},
                "premiere": {"$first": "$premiere"},
                "idMAL": {"$first": "$idMAL"},
            }
        },
        {
            "$sample": {
                "size": int(size) if size else 6
            },
        }
    ])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "report", methods=["POST"])
def report():
    data = request.get_json(silent=True)
    report_dict = {"series": data["series"], "episode": data["episode"]}
    report_collection.insert_one(report_dict)

    return Response(response={"success": True}, status=200, mimetype="application/json")


@app.route(BASE_URL + "calendar")
def getBroadcast():
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "title": {"$first": "$title"},
                "airing": {"$first": "$airing"},
                "broadcast": {"$first": "$broadcast"},
            }
        },
        {"$match": {"airing": {"$eq": True}}}
    ])

    data = list(filter(lambda x: x["broadcast"] != "Unknown", query))

    calendar = {
        "mon": [],
        "tue": [],
        "wed": [],
        "thu": [],
        "fri": [],
        "sat": [],
        "sun": []
    }

    days = []
    for anime in data:
        days.append(
            {
                "series": anime["_id"]["series"],
                "title": anime["title"],
                "broadcast": convertJST(anime["broadcast"])
            })

    for element in days:
        day = element["broadcast"][0]
        hours = element["broadcast"][1]
        series = element["series"]
        title = element["title"]

        calendar[day].append({"series": series, "hours": hours, "title": title})

    return dumps(calendar)


@app.route(BASE_URL + "top")
def getTopAnimes():
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "title": {"$first": "$title"},
                "title_romaji": {"$first": "$title_romaji"},
                "updated": {"$first": "$updated"},
                "airing": {"$first": "$airing"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "score": {"$first": "$score"},
                "premiere": {"$first": "$premiere"},
                "count": {"$sum": 1},
            }
        }
    ])

    query = sorted(query, key=lambda x: float(x["score"] or 0.00))
    query = list(reversed(query))

    data = json(query[:50])
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "upcoming")
def getUpcomingAnimes():
    query = collection.aggregate([
        {
            "$group": {
                "_id": {"series": "$series"},
                "pretty": {"$first": "$series_pretty"},
                "title": {"$first": "$title"},
                "updated": {"$first": "$updated"},
                "upcoming": {"$first": "$upcoming"},
                "pic": {"$first": "$pic"},
                "thumb": {"$first": "$thumb"},
                "count": {"$sum": 1},
            }
        },
        {"$match": {"upcoming": {"$eq": True}}}
    ])

    query = sorted(query, key=lambda x: x["pretty"])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")
