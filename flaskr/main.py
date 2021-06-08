from datetime import datetime, timedelta
from flask import Flask, Response, request, render_template
from flask_cors import CORS
from flask_compress import Compress
from flaskr.db.connect_db import connect
from flaskr.utils.helpers import compareJSONdate, convertJST
from bson.json_util import dumps as json
from json import dumps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config["COMPRESS_ALGORITHM"] = "br"

# rate limiter for everyone excluding AnimeAndromeda and localhost (for testing)
limiter = Limiter(
    app,
    key_func=lambda: "" if get_remote_address() == "127.0.0.1" or get_remote_address() == "76.76.21.21"
    else get_remote_address(),
    default_limits=["25 per minute"]
)


BASE_URL = "/api/v2/anime/"

client = connect()
db = client["andromeda_dev"]
db_report = client["andromeda"]
collection = db["anime_docs"]
report_collection = db_report["reports"]

# Access-Control-Allow-Origin: *
CORS(app)
# Use brotli compression
Compress(app)


@app.route("/")
@app.route("/api/v2/")
@limiter.limit("10 per minute")
def index():
    print(get_remote_address())
    return render_template('index.html')


@app.route(BASE_URL + "get/<id>")
def getAnime(id):
    query = collection.find(
        {"$or": [
            {"series_pretty": id},
            {"series": id},
            {"title": id},
        ]})

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "genre/<genres>")
@app.route(BASE_URL + "filter/<genres>")
@app.route(BASE_URL + "filter/<genres>/<year>")
def getAnimeByGenres(genres, year=""):

    if year != "" and len(year) != 4:
        return Response(response=json([]), status=200, mimetype="application/json")

    genres_list = []
    if "," in genres:
        genres_list = genres.split(",")
    else:
        genres_list.append(genres)

    query = collection.find({
        "$and": [
            {"genres": {"$all": genres_list}},
            {"premiere": {"$regex": year}}
        ]
    })

    query = sorted(query, key=lambda x: x["series_pretty"])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "year/")
@app.route(BASE_URL + "year/<year>")
def getAnimeByYear(year=""):
    if len(year) != 4:
        return Response(response=json([]), status=200, mimetype="application/json")

    query = collection.find({"premiere": {"$regex": year}})

    query = sorted(query, key=lambda x: x["series_pretty"])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "search/")
@app.route(BASE_URL + "search/<id>")
@limiter.limit("100 per minute")
def searchAnime(id=""):
    if id == "":
        return Response(response=dumps([]), status=200, mimetype="application/json")

    query = collection.find({
        "$or": [
            {"series_pretty": {"$regex": id, "$options": "i"}},
            {"title": {"$regex": id, "$options": "i"}},
            {"title_romaji": {"$regex": id, "$options": "i"}},
        ],
    })

    query = sorted(query, key=lambda x: x["series_pretty"])

    # add count and sanitize
    for anime in query:
        anime['count'] = len(dict(anime['eps']).keys())
        anime.pop('__v', None)
        anime.pop('eps', None)
        anime.pop('desc', None)
        anime.pop('genres', None)
        anime.pop('trailer', None)
        anime.pop('duration', None)
        anime.pop('broadcast', None)

    return Response(response=json(query), status=200, mimetype="application/json")


@app.route(BASE_URL + "latest")
def getLatestAnimes():
    query = collection.find(
        {"updated": {"$gte": datetime.now() - timedelta(weeks=9)}})

    query = sorted(query, key=lambda x: compareJSONdate(
        x["updated"]), reverse=True)

    data = json(query[:12])
    return Response(response=data, status=200, mimetype="application/json")


@DeprecationWarning
@app.route(BASE_URL + "latest/aired")
def getLastAiredAnimes():
    return Response(response=json("This route has been deprecated"), status=200, mimetype="application/json")


@app.route(BASE_URL + "latest/airing")
def getAiringAnimes():
    query = collection.find({"airing": {"$eq": True}})

    query = sorted(query, key=lambda x: x["series_pretty"])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "random")
def getRandomAnimes():
    size = request.args.get('size')
    query = collection.aggregate([
        {"$match": {"series": {"$exists": True}}},
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
    query = collection.find({"airing": {"$eq": True}})

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
                "series": anime["series"],
                "title": anime["title"],
                "broadcast": convertJST(anime["broadcast"])
            })

    for element in days:
        day = element["broadcast"][0]
        hours = element["broadcast"][1]
        series = element["series"]
        title = element["title"]

        calendar[day].append(
            {"series": series, "hours": hours, "title": title})

    return Response(response=dumps(calendar), status=200, mimetype="application/json")


@app.route(BASE_URL + "top")
def getTopAnimes():
    query = collection.find(
        {"score": {"$gte": "7.5"}})

    query = sorted(query, key=lambda x: float(x["score"] or 0.00))
    query = list(reversed(query))

    data = json(query[:50])
    return Response(response=data, status=200, mimetype="application/json")


@app.route(BASE_URL + "upcoming")
def getUpcomingAnimes():
    query = collection.find({"upcoming": {"$eq": True}})

    query = sorted(query, key=lambda x: x["series_pretty"])

    data = json(query)
    return Response(response=data, status=200, mimetype="application/json")
