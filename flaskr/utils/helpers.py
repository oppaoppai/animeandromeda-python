from datetime import datetime
from flaskr.data.domains import days


def compareJSONdate(jsondate):
    date = str(jsondate)
    if "Z" in date:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")  # is json date
    elif date == "None":
        return datetime(1, 1, 1, 0, 0)  # isn't either json or timezone dateobj
    else:
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")  # has timezone


def convertEpisode(ep):
    # if episode is a special (multiple episodes in a single one)
    if "-" in ep:
        parsed = int(ep.split("-")[0])
        return (0, parsed, '')
    else:
        # mixed list comparator
        try:
            parsed = int(ep)
            return (0, parsed, '')
        except ValueError:
            return (1, ep, '')


def convertJST(jst):
    # get the CET time from a formatted String in JST time. ex: Tuesdays at 21:54 (JST) -> ["tue", "14:54"]
    formatter = "%H:%M"
    parts = jst.split(" ")
    try:
        day_of_week = parts[0]
        hours = parts[2]
    except IndexError:
        # soluzione temporanea
        # attenzione perché fa schifo, la strategia è andare a sistemare lo schifo sul database
        print("wrong format")
        hours = "7:00"
        day_of_week = "Sundays"

    #delta from italy
    jst_delta = "7:00"

    correct_time = str(
        datetime.strptime(hours, formatter) -
        datetime.strptime(jst_delta, formatter))

    if "-1 day" in correct_time:
        day_index = (list(days.keys()).index(day_of_week))
        return [
            days[list(days.keys())[day_index - 1]],
            correct_time.split(",")[1].lstrip()
        ]

    return [days[day_of_week], correct_time]
