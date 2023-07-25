try:
    import __updir__
except Exception:
    pass
import util
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import backref
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import text, func, update, bindparam
from sqlalchemy.sql import exists
from sqlalchemy.dialects.postgresql import JSONB, insert, ARRAY
from sqlalchemy import Column, Integer, Boolean, String, DateTime
from sqlalchemy import Table, ForeignKey, UniqueConstraint, ForeignKeyConstraint, Sequence
import datetime
from models import mv_model
import time

indexes = {}

# If there isn't an index for the card, create one by doing chr(ord(last_row)+1)
def create_card_index(session, card_name):
    if not indexes:
        for card_index in session.query(mv_model.T_CARD_INDEX).all():
            indexes[card_index.name] = card_index.index
    found = indexes.get(card_name, None)
    if not found:
        count = len(indexes.keys())
        print(count)
        index = chr(count+1)
        print(repr(f"created index {index}"))
        session.add(mv_model.T_CARD_INDEX(index=index, name=card_name))
        indexes[card_name] = index
        return index
    return found


def create_card_indexes():
    print("start creating index")
    with mv_model.Session() as session:
        for card in session.query(mv_model.Card).all():
            create_card_index(session, card.name)
        print("start commiting")
        session.commit()


def create_deck_index(session, deck, update=False):
    card_string = []
    for card in deck.get_cards():
        index = create_card_index(session, card.name)
        card_string.append(index)
    card_string = "".join(sorted(card_string))
    existing = session.query(mv_model.T_DECK_CARDS).filter(mv_model.T_DECK_CARDS.deck_key==deck.key).first()
    if not existing:
        existing = mv_model.T_DECK_CARDS(deck_key=deck.key, cards=card_string)
    else:
        if not update:
            return
        existing.cards = card_string
    session.add(existing)
    return existing

def create_deck_indexes():
    print("starting to index decks... might take some time")
    page_size = 100
    for deck_index in range(30094, int(3009614/page_size)):
        with mv_model.Session() as session:
            print(f"--INDEXING page {deck_index}--")
            new = []
            for deck in session.query(mv_model.Deck).order_by(mv_model.Deck.global_index).limit(page_size).offset(deck_index*page_size):
                inserted = create_deck_index(session, deck)
                if inserted:
                    new.append(inserted)
            if new:
                print("inserted", repr([deck.deck_key for deck in new]))
                session.commit()
                time.sleep(5)


def card_search(card_list=[]):
    card_indexes = []
    with mv_model.Session() as session:
        for card_name, count in card_list:
            card_indexes.append(create_card_index(session, card_name) * count)
        print(card_indexes)
        q = session.query(mv_model.T_DECK_CARDS)
        for index in card_indexes:
            q = q.filter(mv_model.T_DECK_CARDS.cards.like(f"%{index}%"))
        for deck in q.limit(15).all():
            print(deck.deck_key, deck.cards)

#create_deck_indexes()
#card_search([('Murmook', 1)])