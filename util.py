import requests
import re
SEPARATOR = " • "


def dequote(t):
    quotes = ['“', '”']
    while '"' in t:
        next = quotes.pop(0)
        t = t.replace('"', next, 1)
        quotes.append(next)
    t = t.replace("'","\u2019")
    return t


def sanitize_deck_name(name):
    name_sane = name.lower()
    name_sane = re.sub("[^(\w| )]+", "", name_sane)
    return name_sane


cargo_cache = {}

def cache_key(url, params):
    k = url
    for key in sorted(params.keys()):
        k += '__..'+str(params[key])
    return k


def cargo_query(search_params):
    params = {
        "action": "cargoquery",
        "format": "json",
        "limit": 500  # Really should page the query
    }
    params.update(search_params)
    key = cache_key("https://archonarcana.com/api.php", params)
    if key in cargo_cache:
        return cargo_cache[key]
    r = requests.get("https://archonarcana.com/api.php", params=params)
    j = r.json()
    print(j)
    print(j['cargoquery'])
    cargo_cache[key] = j
    return j
