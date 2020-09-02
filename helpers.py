from datetime import datetime


def compareJSONdate(jsondate):
    date = str(jsondate)
    if "Z" in date:
        return datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%S.%fZ")  # is json date
    elif date == "None":
        return datetime(1, 1, 1, 0, 0)     # isn't either json or timezone dateobj
    else:
        return datetime.strptime(
            date, "%Y-%m-%d %H:%M:%S.%f")  # has timezone


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
