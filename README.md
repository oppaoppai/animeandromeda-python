# animeandromeda-python

![logo](https://www.animeandromeda.net/static/media/Illustration.b4a9d51c.webp)

# Rachnera: AnimeAndromeda Public API
<img src="https://i.ibb.co/z6FwkMV/rachnera.png" width="400">

AnimeAndromeda REST API built upon Flask and MongoDB native python driver

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
curl http://localhost:5000/api/v2/anime/search/konOsU
```json
[
  {
    "_id": {
      "$oid": "60bf7ba2cd13e023bc0963d9"
    },
    "updated": {
      "$date": 1596706208092
    },
    "series": "KonoSubarashiiSekaiNiShukufukuWo",
    "series_pretty": "Kono Subarashii Sekai Ni Shukufuku Wo",
    "title": "KonoSuba: God's Blessing on This Wonderful World!",
    "title_romaji": "Kono Subarashii Sekai ni Shukufuku wo!",
    "pic": "https://cdn.myanimelist.net/images/anime/8/77831l.jpg",
    "aired": "Jan 14, 2016 to Mar 17, 2016",
    "airing": false,
    "score": "8.16",
    "premiere": "Winter 2016",
    "count": 12
  },
  {
    "_id": {
      "$oid": "60bf7ba2cd13e023bc0963e1"
    },
    "updated": {
      "$date": 1596706208095
    },
    "series": "KonoSubarashiiSekaiNiShukufukuWo2",
    "series_pretty": "Kono Subarashii Sekai Ni Shukufuku Wo 2",
    "title": "KonoSuba: God's Blessing on This Wonderful World! 2",
    "title_romaji": "Kono Subarashii Sekai ni Shukufuku wo! 2",
    "pic": "https://cdn.myanimelist.net/images/anime/2/83188l.jpg",
    "aired": "Jan 12, 2017 to Mar 16, 2017",
    "airing": false,
    "idMAL": "32937",
    "score": "8.33",
    "premiere": "Winter 2017",
    "count": 11
  },
  {
    "_id": {
      "$oid": "60bf7bbfcd13e023bc0965a8"
    },
    "updated": {
      "$date": 1598019740129
    },
    "series": "KonoSubaMovie",
    "series_pretty": "KonoSuba movie: Legend of crimson",
    "title": "KONOSUBA -God's blessing on this wonderful world!- Legend of Crimson",
    "title_romaji": "Kono Subarashii Sekai ni Shukufuku wo!: Kurenai Densetsu",
    "pic": "https://cdn.myanimelist.net/images/anime/1856/100031l.jpg",
    "aired": "Aug 30, 2019",
    "airing": false,
    "idMAL": "38040",
    "premiere": null,
    "count": 1
  }
]
```

##### `search/`
clears the search => returns an empty list

##### `latest/`
returns a list of the latest inserted anime into the db
(not so useful outside the website)

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
`uwsgi --enable-threads
   --threads 2
   --ini rachnera.ini`  
__single-threaded__:  
 `uwsgi --ini rachnera.ini`

Then put the application behind a proxy, heres an example for nginx:
```
#ANIMEANDROMEDA API
server {
        listen 443 ssl http2;
        server_name your domain;
        ssl_session_cache  builtin:1000  shared:SSL:10m;
        ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
        ssl_prefer_server_ciphers on;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/path/to/application/rachnera-animeandromeda/rachnera.sock;
        }

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
}
```   
## DB Schema
```
{
    _id: String
    updated: Date
    series: String
    eps: Map<String, String>
    url: String
    series_pretty: String
    aired: String
    desc: String
    genres: Array
    idMAL: Int32
    pic: String
    thumb: String
    title: String
    airing: false
    duration: String
    title_romaji: String
    trailer: String
    broadcast: String
    score: String
    premiere: String
    fanSub: String
}
```
here's an example:
```json
{
    "_id": "5f318a11c3e430777dsadbff",
    "updated": "2020-08-10T17:55:13.916Z",
    "series": "KanojoOkarishimasu",
    "series_pretty": "Kanojo, Okarishimasu",
    "eps": {
      "01": "https://streaming-endpoint.tld/xx.mp4",
      "02": "https://streaming-endpoint.tld/xx.mp4",
      "03": "https://streaming-endpoint.tld/xx.mp4",
      "04": "https://streaming-endpoint.tld/xx.mp4"
    },
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
