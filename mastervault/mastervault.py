import __updir__
import passwords
import random
import json
import sys
import time
import requests
import util
import re
from sqlalchemy import and_
from models import mv_model
import threading
from hanging_threads import start_monitoring

def wait(seconds,reason=""):
    print(" -waiting",seconds,"for",reason)
    time.sleep(seconds)
    print(" -waited",seconds,"for",reason)

def rget(*args, **kwargs):
    print("    req", args, kwargs)
    if "timeout" not in kwargs:
        kwargs["timeout"] = 10
    resp = requests.get(*args, **kwargs)
    print("    -resp", args, kwargs)
    return resp

def correlate_deck(deck, cards_by_key, cards_by_key_exp):
    for card_key in deck["_links"]["cards"]:
        card = {}
        card.update(cards_by_key[card_key])
        card["deck_expansion"] = deck["expansion"]
        card["is_legacy"] = card_key in deck["set_era_cards"]["Legacy"]
        cards_by_key_exp[(card_key, deck["expansion"])] = card


class RateLimitException(Exception):
    pass


def get_json(resp):
    try:
        j = resp.json()
    except Exception:
        raise
    if j.get("code", None) == 429:
        raise RateLimitException("Hit code 429", j)
    return j


def proxy_orbit():
    proxy = rget("https://api.proxyorbit.com/v1/?twitter=true&ssl=true&token="+passwords.PROXY_ORBIT_KEY)
    d = proxy.json()
    if "ip" not in d:
        return None
    return str(d["ip"])+":"+str(d["port"])


def proxy_rotator():
    proxy = rget("http://falcon.proxyrotator.com:51337/?apiKey="+passwords.PROXY_ROTATOR_KEY)
    d = proxy.json()
    if "proxy" not in d:
        return None
    return d["proxy"]


def proxy_spider():
    proxy = rget("https://proxy-spider.com/api/proxies.json?api_key=%s&order=random&limit=1&page=1&supports=get&protocols=https&response_time=slow,medium,fast&type=anonymous,elite,transparent&country_code=null&test=0" % passwords.PROXY_SPIDER_KEY)
    d = proxy.json()
    if "data" not in d or "proxies" not in d["data"]:
        return None
    pd = d["data"]["proxies"][0]
    return str(pd["ip"])+":"+str(pd["port"])


def get_proxy_list():
    proxy = rget("https://api.getproxylist.com/proxy")
    d = proxy.json()
    if "ip" not in d:
        return None
    return str(d["ip"])+":"+str(d["port"])

def proxy_list1():
    # from https://proxyscrape.com/premium?ref=topfpl
    with open("data/proxy_list1.txt") as f:
        urls = f.read().split("\n")
        return random.choice(urls)
    return None

def sslproxy():
    from fp.fp import FreeProxy
    try:
        return FreeProxy(rand=True).get()
    except Exception:
        return None


def blazingproxy():
    with open("data/blazing_proxy.txt") as f:
        urls = f.read().split("\n")
        return random.choice(urls)


# TODO - the scraper itself could record this from its normal api calls
def get_mastervault_deck_count():
    """This is how we can detect how far off in the scrape we are"""
    r = requests.get("https://www.keyforgegame.com/api/decks/count", headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
    })
    count = r.json()['count']
    return count


class MasterVault:
    def __init__(self):
        self.last_call = None
        self.max_page = 24
        self.scope = mv_model.UpdateScope()
        self.thread_states = {}
        self.insert_lock = threading.Lock()
        self.last_locale_call = None

    def proxyget(self, *args, **kwargs):
        lastexc = None
        timeout=20
        def good_proxy():
            return self.scope.get_proxy()
        methods = []#(proxy_rotator, 1), (good_proxy, 1), (sslproxy, 1), (proxy_list1, 1)]
        random.shuffle(methods)
        for method, tries in methods:
            proxy = {"method": method.__name__}
            for i in range(tries):
                url = method()
                if not url:
                    break
                proxy['url'] = url
                try:
                    r = rget(proxies={'http':url, 'https':url}, 
                                     timeout=timeout, *args, **kwargs)
                    self.scope.add_proxy(url)
                except Exception as exc:
                    lastexc = exc
                    self.scope.remove_proxy(url)
                    print("error", kwargs['params']['page'], method.__name__)
                    continue
                try:
                    return get_json(r), proxy
                except Exception as exc:
                    print("error", kwargs['params']['page'], method.__name__)
                    lastexc = exc
        wait(20)
        try:
            r = rget(timeout=timeout, *args, **kwargs)
        except Exception as exc:
            lastexc = exc
            wait(1)
            print("error", kwargs['params']['page'], "raw1")
            raise
        try:
            j = get_json(r)
            return j, {"method":"unproxied"}
        except Exception as exc:
            print("error", kwargs['params']['page'], "raw2")
            lastexc = exc
            wait(5)
            raise
        print(lastexc)
        raise Exception("Couldn't get valid response")

    def _call(self, endpoint, args, lang="en-US"):
        assert endpoint in ['decks']
        url = "https://www.keyforgegame.com/api/%s/" % endpoint
        key = url+";params:"+json.dumps(args, sort_keys=True)
        return self.proxyget(url, params=args, headers={"Accept-Language": lang}, cookies={"lang":lang})

    def get_deck(self, deck_name):
        args = {
            "page": 1,
            "page_size": 1,
            "search": deck_name,
            "power_level": "0,11",
            "chains": "0,24",
            "ordering": "-date"
        }
        dat, proxy = self._call("decks", args)
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

    def get_decks_with_cards(self, direction, page, lang="en-us", page_size=None):
        if not page_size:
            page_size = self.max_page
        args = {
            "page": page,
            "page_size": page_size,
            "power_level": "0,11",
            "chains": "0,24",
            "ordering": direction+"date",
            "links": "cards"
        }
        dat, proxy = self._call("decks", args, lang)
        if "data" not in dat:
            return [], [], []
        decks = dat["data"]
        cards = dat["_linked"]["cards"]
        cards_by_key = {}
        for card in cards:
            cards_by_key[card["id"]] = card
        cards_by_key_exp = {}
        [correlate_deck(deck, cards_by_key, cards_by_key_exp) for deck in decks]
        return decks, list(cards_by_key_exp.values()), proxy

    def insert(self, decks, cards, page):
        with self.insert_lock:
            self.scope.begin()
            [self.scope.add_deck(
                    key = deck['id'],
                    name = deck['name'],
                    expansion = deck['expansion'],
                    data = deck,
                    page = page,
                    index = i
                ) for (i,deck) in enumerate(decks)]
            [self.scope.add_card(
                    key = card['id'],
                    name = card['card_title'],
                    deck_expansion = card['deck_expansion'],
                    data = card
                ) for card in cards]
            self.scope.commit()

    def scrape_back(self, start_at=1, thread_index=0):
        """Start scraping decks from the oldest to the newest
        The first deck we hit that we don't know about starts the scrape proper
        After the proper scrape begins, if we hit a deck we know about, we've caught
        up to the front scraper and can stop.
        
        We can also save which page we left off on and resume the back scrape from there"""
        self.thread_states[thread_index] = ["", start_at]
        wait(random.randint(0,10))
        while 1:
            print("threads",repr(self.thread_states))
            self.thread_states[thread_index][0] = "ok_open"
            print("Before check next page")
            try:
                with self.insert_lock:
                    page = self.scope.next_page_to_scrape(start_at)
            except Exception:
                self.thread_states[thread_index][0] = "fail_start"
                wait(1)
                continue
            self.thread_states[thread_index] = ["ok_scrape", page]
            print("start starting")
            if not self.scope.start_page(page=page):
                print("error")
                wait(2)
                continue
            print("SCRAPE PAGE",page,"thread:",thread_index)
            try:
                decks, cards, proxy = self.get_decks_with_cards("", page)
            except Exception:
                import traceback
                traceback.print_exc()
                self.thread_states[thread_index][0] = "fail_api_call"
                with self.insert_lock:
                    self.scope.clean_scrape(page)
                wait(1)
                continue
            if not decks or len(decks)<1:
                self.thread_states[thread_index][0] = "ok_done"
                with self.insert_lock:
                    self.scope.clean_scrape(page)
                print("#### - didn't get decks on page %d" % page)
                wait(60)
                continue
            try:
                self.insert(decks, cards, page)
                self.thread_states[thread_index][0] = "ok_inserted"
            except Exception:
                wait(1)
                self.thread_states[thread_index][0] = "fail_insert"
                raise
                continue
            print("########### inserted",len(decks),"decks, and",len(cards),"cards from page",page,"via",proxy, len(threading.enumerate()))
            if len(decks)<24:
                with self.insert_lock:
                    self.scope.clean_scrape(page)
                print("#### - didn't get 24 decks on page %d" % page)
                wait(60)
                continue
            self.scope.scraped_page(page=page, decks_scraped=len(decks), cards_scraped=len(cards))
            self.thread_states[thread_index][0] = "ok_continue"
            wait(1)
        return True
    
    def scrape_cards_locale(self, locale, card_title=None, rescrape=False):
        """Updates card definitions by retriving the decks that contain the cards using the given locale"""
        #Get all cards that need to be updated... all cards
        session = mv_model.Session()
        if rescrape:
            query = session.query(mv_model.Card)
        else:
            query = session.query(mv_model.Card, mv_model.LocaleCard)
        if card_title:
            query = query.filter(mv_model.Card.name==card_title)
        def lookat_card(card):
            return (
                not (card.data["is_maverick"] or card.data["is_enhanced"]) or 
                (card.name in ["Exchange Officer"] and card.data["house"] == "Dis")
            )
        if not rescrape:
            query = query.outerjoin(mv_model.LocaleCard, and_(mv_model.LocaleCard.en_name==mv_model.Card.name,mv_model.LocaleCard.locale==locale))
            print(query)
            cards = [row[0] for row in query.all()
                if not row[1] and lookat_card(row[0])
            ]
        else:
            cards = [card for card in query.all() if lookat_card(card)]

        deck_pages = {}
        handled_cards = {}
        #For each card, find a deck that it has and that decks page. 
        for i,card in enumerate(cards):
            print(i,"/",len(cards))
            if card.key in handled_cards:
                continue
            decks = session.query(mv_model.DeckCard).filter(mv_model.DeckCard.card_key==card.key).limit(1)
            deck_key = decks.first().deck_key
            deck = session.query(mv_model.Deck).filter(mv_model.Deck.key==deck_key).first()
            page = deck.page
            deck_pages[page] = 1
            # For each card that is on that decks page, mark it as handled if we update that page
            for deck in session.query(mv_model.Deck).filter(mv_model.Deck.page==page).all():
                for card_id in deck.data["_links"]["cards"]:
                    handled_cards[card_id] = 1

        #Pull the selected pages from mv and update the cards with the right locale
        for i,page in enumerate(sorted(deck_pages.keys())):
            print("GET PAGE", page, i, '/', len(deck_pages.keys()))
            while 1:
                try:
                    while self.last_locale_call and time.time()-self.last_locale_call < 10:
                        time.sleep(1)
                    self.last_locale_call = time.time()
                    decks, cards, proxy = self.get_decks_with_cards("", page, locale)
                    update_cards = []
                    for card in cards:
                        if card["is_legacy"]:
                            continue
                        en_card = session.query(mv_model.Card).filter(mv_model.Card.key==card["id"]).first()
                        locale_card = mv_model.LocaleCard(en_name=en_card.name, key=card["id"], data=card, locale=locale, deck_expansion=card["deck_expansion"])
                        update_cards.append(locale_card)
                    print("adding", len(cards))
                    mv_model.postgres_upsert(session, mv_model.LocaleCard, update_cards)
                    session.commit()
                    break
                except:
                    time.sleep(10)

    def scrape_next_task(self):
        """Pick next page to scrape from the tasks. If one exists, and we scrape the right
        number of decks, record the task as complete."""
        wait(random.randint(0,10))
        while 1:
            try:
                with self.insert_lock:
                    task = self.scope.next_scrape_task()
            except Exception:
                wait(1)
                continue
            if not task:
                print("No task found. Wait(120)")
                wait(120)
                continue
            print("next task SCRAPE PAGE",task.page)
            try:
                decks, cards, proxy = self.get_decks_with_cards("", task.page, "en-us", task.per_page)
            except Exception:
                import traceback
                traceback.print_exc()
                continue
            if not decks or len(decks)<1:
                print("#### - next task didn't get decks on page %d" % task.page)
                wait(60)
                continue
            try:
                self.insert(decks, cards, task.page)
            except Exception:
                wait(1)
                raise
                continue
            print("########### next task inserted",len(decks),"decks, and",len(cards),"cards from page",task.page,"via",proxy, len(threading.enumerate()))
            if len(decks)<task.per_page:
                print("#### - next task didn't get %d decks on page %d" % (task.per_page, task.page))
                wait(60)
                continue
            self.scope.scraped_page_task(task=task, decks_scraped=len(decks), cards_scraped=len(cards))
            wait(1)
        return True



mv = MasterVault()


def master_vault_lookup(deck_name):
    deck_name = util.dequote(deck_name)
    deck = mv.get_deck(deck_name)
    if not deck:
        deck = mv.get_deck(util.dequote(deck_name))
    if not deck:
        raise Exception("No deck found", deck_name)
    return deck


def daemon(mode="back_scrape", starts=[1]):
    threads = []
    mv = MasterVault()
    for start in starts:
        def mv_thread():
            print("thread open")
            if mode == "back_scrape":
                mv.scrape_back(start, start)
            elif mode == "tasks":
                mv.scrape_next_task()
            print("thread close")
        t = threading.Thread(target=mv_thread)
        threads.append(t)
        t.start()
    #t = threading.Thread(target=workers.thread)
    #threads.append(t)
    #t.start()
    print("start monitoring")
    monitoring_thread = start_monitoring(seconds_frozen=30)


if __name__ == "__main__":
    print(sys.argv)
    if sys.argv[1] == "get_locale":
        print(mv.scrape_cards_locale(sys.argv[2]))
    elif sys.argv[1] == "tasks":
        daemon("tasks", [1])
    else:
        #daemon("back_scrape", [int(x) for x in sys.argv[1:]])
        daemon("tasks", [1])
