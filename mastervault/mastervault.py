import json
import os
import time
import requests
try:
    import util
except Exception:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import util


class MasterVault(object):
    def __init__(self):
        self.last_call = None
        self.call_wait = 10
        self.max_page = 24
        self.cache = {}
        if os.path.exists("mv.cache"):
            with open("mv.cache") as f:
                self.cache = json.loads(f.read())

    def sleep(self):
        if not self.last_call:
            self.last_call = time.time()-self.call_wait
        dt = time.time()-self.last_call
        print(dt)
        if dt < self.call_wait:
            time.sleep(self.call_wait-dt)

    def save_cache(self, key, value):
        self.cache[key] = value
        #with open("mv.cache", "w") as f:
        #    f.write(json.dumps(self.cache))

    def _call(self, endpoint, args):
        assert endpoint in ['decks']
        url = "https://www.keyforgegame.com/api/%s/" % endpoint
        key = url+";params:"+json.dumps(args, sort_keys=True)
        if key not in self.cache:
            self.sleep()
            r = requests.get(url, params=args)
            j = r.json()
            self.last_call = time.time()
            if j.get("code", None) == 429:
                raise(Exception(j["message"]+";"+j["detail"]))
            self.save_cache(key, j)
        return self.cache[key]

    def get_deck(self, deck_name):
        args = {
            "page": 1,
            "page_size": 1,
            "search": deck_name,
            "power_level": "0,11",
            "chains": "0,24",
            "ordering": "-date"
        }
        dat = self._call("decks", args)
        if "data" not in dat:
            raise Exception("No data found", deck_name)
        if len(dat["data"]) > 1:
            raise Exception("Too many decks found")
        if not dat["data"]:
            return None
        deck_data = dat["data"][0]
        return {
            "url": "https://www.keyforgegame.com/deck-details/%(id)s" % {"id": deck_data["id"]}
        }

    def get_decks_with_cards(self):
        card_names = {}
        decks = []
        for page in range(1, 100):
            args = {
                "page": page,
                "page_size": self.max_page,
                "power_level": "0,11",
                "chains": "0,24",
                "ordering": "-date",
                "links": "cards"
            }
            dat = self._call("decks", args)
            decks.extend(dat["data"])
            cards = dat["_linked"]["cards"]
            for card in cards:
                name = card["card_title"]
                if name not in card_names:
                    card_names[name] = {}
                card_names[name][card["id"]] = card
                if len(card_names[name]) > 1:
                    print(card_names[name])
            print(len(decks))

    def scrape_back(self):
        """Start scraping decks from the oldest to the newest
        The first deck we hit that we don't know about starts the scrape proper
        After the proper scrape begins, if we hit a deck we know about, we've caught
        up to the front scraper and can stop.
        
        We can also save which page we left off on and resume the back scrape from there"""

    def scrape_front(self):
        """Start scraping from the front. If we hit a deck we know about, we've
        caught up to our last scrape from the front and can stop"""


mv = MasterVault()


def master_vault_lookup(deck_name):
    deck_name = util.dequote(deck_name)
    deck = mv.get_deck(deck_name)
    if not deck:
        deck = mv.get_deck(util.dequote(deck_name))
    if not deck:
        raise Exception("No deck found", deck_name)
    return deck


if __name__ == "__main__":
    mv.get_decks_with_cards()
