import hug
import sys, os, traceback
import base64
from mastervault import datamodel
import carddb

@hug.not_found()
def not_found_handler():
    return "Not Found"


@hug.get(examples="key=something")
def deck(key=None, name=None):
    print(repr(name))
    session = datamodel.Session()
    deck = session.query(datamodel.Deck)
    if key:
        deck = deck.filter(datamodel.Deck.key==key)
    if name:
        deck = deck.filter(datamodel.Deck.name==name)
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

@hug.get("/favicon.ico", output=hug.output_format.file)
def favicon():
    return "mastervault/keymirror.png"