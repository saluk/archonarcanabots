import hug
import sys, os, traceback
import base64
from mastervault import datamodel
from sqlalchemy import or_, and_
import carddb

from hug.middleware import CORSMiddleware

api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))

@hug.not_found()
def not_found_handler():
    return "Not Found"


@hug.get(examples="key=something")
def deck(key=None, name=None, wins=None, id_=None):
    print(repr(name))
    session = datamodel.Session()
    deck = session.query(datamodel.Deck)
    if key:
        deck = deck.filter(datamodel.Deck.key==key)
    if name:
        deck = deck.filter(datamodel.Deck.name==name)
    if id_:
        page = int(int(id_)/24)+1
        index = int(id_)-((page-1)*24)
        print(page,index)
        deck = deck.filter(datamodel.Deck.page==page, datamodel.Deck.index==index)
    deck = deck.first()
    if not deck:
        return "No data"
    cards = []
    for card_key in deck.data['_links']['cards']:
        card = session.query(datamodel.Card).filter(datamodel.Card.key==card_key).first()
        if card:
            card = carddb.add_card(card.data)
            cards.append(card)
        else:
            cards.append((card_key, "no data"))
    d = {'deck_data':{}}
    d['deck_data'].update(deck.data)
    d['meta'] = {'page':deck.page, 'index':deck.index, 'scrape_date':deck.scrape_date}
    d['cards'] = cards
    return d

@hug.get(examples="start=50&end=100&direction=1")
def decks(start=None, end=None, direction=1):
    if not start: start = 0
    if not end: end = 50
    start = int(start)
    end = int(end)
    if start<0:
        start = 0
    if end-start > 1000 or end<start:
        end = start+1000
    if end==start:
        end = start+1
    session = datamodel.Session()
    total = session.execute("select * from decks_count")
    count = total.first()[0]
    left_bound_page = start//int(24)
    left_bound_index = start-left_bound_page*24
    right_bound_page = end//int(24)
    right_bound_index = end-right_bound_page*24
    left_bound_page += 1
    #left_bound_index += 1
    right_bound_page += 1
    #right_bound_index += 1
    deckq = session.query(datamodel.Deck).\
        filter(datamodel.Deck.page>=left_bound_page,datamodel.Deck.page<=right_bound_page).\
        filter(or_(datamodel.Deck.page<right_bound_page,datamodel.Deck.index<=right_bound_index)).\
        filter(or_(datamodel.Deck.page>left_bound_page,datamodel.Deck.index>=left_bound_index)).\
        order_by(datamodel.Deck.page, datamodel.Deck.index)
    decks = deckq.all()
    return {"start": start, "end": end, "max": count, 
            "bounds": [(left_bound_page, left_bound_index), (right_bound_page, right_bound_index)],
            "count":len(decks),
            "decks":[[d.key, d.name, ", ".join(d.data['_links']['houses']), d.data["expansion"]] for d in decks]}

@hug.get('/deck/latest')
def latest():
    session = datamodel.Session()
    query = session.execute("select key from decks where (select max(page) from decks)=page order by index desc limit 1;")
    key = query.first()[0]
    return deck(key)

@hug.get("/favicon.ico", output=hug.output_format.file)
def favicon():
    return "mastervault/keymirror.png"