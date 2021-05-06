# animeandromeda-python

![logo](https://www.animeandromeda.net/static/media/Illustration.23741024.webp)

AnimeAndromeda REST API

## endpoints
fixed prefix: /api/v2/anime/

##### `get/<id>`  
returns a json of episode o a specific anime.
The id is the name of the __exact__ anime series

##### `get/genre/<genres>` 
returns a json of animes with a specified genre
**[here's the genres domain](https://raw.githubusercontent.com/oppaoppai/animeandromeda-react/master/src/globals/domains.js)**

##### `search/<id>`
returns a list of possible animes that __like match__ the given id
example
curl http://localhost:5000/api/v2/anime/konOsU
```json
[
  {
    "_id":{
      "series":"KonoSubaMovie"
    },
    "redundant":"KonoSubaMovie",
    "pretty":"KonoSuba movie: Legend of crimson",
    "title":"KONOSUBA -God's blessing on this wonderful world!- Legend of Crimson",
    "title_romaji":"Kono Subarashii Sekai ni Shukufuku wo!: Kurenai Densetsu",
    "pic":"https://cdn.myanimelist.net/images/anime/1856/100031l.jpg",
    "thumb":"https://i.ibb.co/jvSTxTD/f3e533b89392768c8e07a2a28616e58b.jpg",
    "premiere":null,
    "count":1
  },
  {
    "_id":{
      "series":"KonoSubarashiiSekaiNiShukufukuWo"
    },
    "redundant":"KonoSubarashiiSekaiNiShukufukuWo",
    "pretty":"Kono Subarashii Sekai Ni Shukufuku Wo",
    "title":"KonoSuba: God's Blessing on This Wonderful World!",
    "title_romaji":"Kono Subarashii Sekai ni Shukufuku wo!",
    "pic":"https://cdn.myanimelist.net/images/anime/8/77831l.jpg",
    "thumb":"https://i.ibb.co/hW1S1kp/39894.jpg",
    "premiere":"Winter 2016",
    "count":23
  },
  {
    "_id":{
      "series":"KonoSubarashiiSekaiNiShukufukuWo2"
    },
    "redundant":"KonoSubarashiiSekaiNiShukufukuWo2",
    "pretty":"Kono Subarashii Sekai Ni Shukufuku Wo 2",
    "title":"KonoSuba: God's Blessing on This Wonderful World! 2",
    "title_romaji":"Kono Subarashii Sekai ni Shukufuku wo! 2",
    "pic":"https://cdn.myanimelist.net/images/anime/2/83188l.jpg",
    "thumb":"https://i.ibb.co/9YBS7Xt/46002.png",
    "premiere":"Winter 2017",
    "count":11
  }
]
```

##### `search/`
clears the search => returns an empty list

##### `latest/`
returns a list of the latest inserted anime into the db
(not so useful outside the website)

##### `latest/aired`
returns a list of the latest aired animes

##### `latest/airing`
returns a list of the current airing animes

##### `random/`
##### `random?size=*size of the response list*/`
returns a random list of animes
if not specified by the GET parameter the list's size is 6

##### `top/`
returns a list of animes with best scores

##### `upcoming/`
returns a list of upcoming animes
__it's still in development__

## classic setup
- currently tested only on Linux
- clone this repository
- python3 needed and python3-venv or python-virtualenv
  (python3.7 and python3.8 tested)

`cd into the project's directory`  
`python3 -m venv .`  
`chmod +x ./bin/activate`  
`source ./bin/activate`  
`pip install -r requierements.txt`  
`flask run (for testing)`  

For production:  
__multi-threaded__:  
`uwsgi --socket 0.0.0.0:5000
--protocol=http
   --master
   --enable-threads
   --threads 2
   --thunder-lock
   -w app:app`  
__single-threaded__:  
 `uwsgi --socket 0.0.0.0:5000
   --protocol=http
   --master 
   -w app:app`

## docker setup
`cd into the project's directory`  
`docker build -f Dockerfile -t animeandromeda-py .`  
`docker run -d -p 5000:5000 animeandromeda-py`  
or  
`cd into the project's directory`  
`docker build -f Dockerfile -t animeandromeda-py .`  
`docker create --name animeandromeda-py -p 5000:5000 animeandromeda-py`  
`docker start animeandromeda-py`  

__The connection to the database is NOT provided.__
__You have to build your onw database with a schema like this__
```json
{
    _id: String
    updated: Date
    series: String
    ep: String
    url: String
    __v: Int32
    series_pretty: String
    aired: String
    desc: String
    genres: Array
    idMAL: Int32
    pic: String
    thumb: String
    title: String
    airedLast: Date
    airing: false
    airedFirst: Date
    duration: String
    title_romaji: String
    trailer: String
    broadcast: String
    score: String
    premiere: String
}
```
here's an example
```json
{
    "_id": "5f318a11c3e430777dsadbff",
    "updated": "2020-08-10T17:55:13.916Z",
    "series": "KanojoOkarishimasu",
    "series_pretty": "Kanojo, Okarishimasu",
    "ep": "04",
    "url": "https://streaming-endpoint.tld/KanojoOkarishimasu_Ep_04_SUB_xx.mp4",
    "__v": 0,
    "aired": "Jul 11, 2020 to Sep 26, 2020",
    "desc": "Kazuya Kinoshita \r\n blah blah",
    "genres": [
        "Comedy",
        "Romance",
        "School",
        "Shounen"
    ],
    "idMAL": "40839",
    "pic": "https://cdn.myanimelist.net/images/anime/1485/107693l.jpg",
    "title": "Rent-a-Girlfriend",
    "airing": false,
    "thumb": "https://i.ibb.co/jHZC4s3/EY1-JYr-VAAAWIWb-CUnet-noise-scale-Level1-x2.jpg",
    "airedFirst": {
        "$date": "2020-07-11T00:00:00.000Z"
    },
    "airedLast": {
        "$date": "2020-09-26T00:00:00.000Z"
    },
    "duration": "24 min per ep",
    "title_romaji": "Kanojo, Okarishimasu",
    "trailer": "https://www.youtube.com/embed/uIfxrlJg0Jw?enablejsapi=1&wmode=opaque&autoplay=1",
    "broadcast": "Saturdays at 01:25 (JST)",
    "score": "7.2",
    "premiere": "Summer 2020"
}
```
Contatcs:  
Twitter: @Yun_sdvx
