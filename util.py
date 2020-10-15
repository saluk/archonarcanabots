import requests
SEPARATOR = " • "


def dequote(t):
    quotes = ['“', '”']
    while '"' in t:
        next = quotes.pop(0)
        t = t.replace('"', next, 1)
        quotes.append(next)
    t = t.replace("'","\u2019")
    return t


def cargo_query(search_params):
    start = "/api.php?action=cargoquery&format=json"
    params = {
        "action": "cargoquery",
        "format": "json",
        "limit": 500  # Really should page the query
    }
    params.update(search_params)
    r = requests.get("https://archonarcana.com/api.php", params=params)
    print(len(r.json()['cargoquery']))
    return r.json()