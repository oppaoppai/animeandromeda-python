from datetime import datetime


def compareJSONdate(jsondate):
    date = str(jsondate)
    if "Z" in date:
        return datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%S.%fZ")
    elif date == "None":
        return datetime(1, 1, 1, 0, 0)
    else:
        return datetime.strptime(
            date, "%Y-%m-%d %H:%M:%S.%f")
