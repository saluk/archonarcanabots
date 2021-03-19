import os
import json
import time

from sqlalchemy.sql.expression import bindparam
import __updir__
from models import wiki_card_db, mv_model
from sqlalchemy.sql import and_, not_, func, update
from models import shared


session = mv_model.Session()

def fix_scrape_dates():
    from datetime import datetime, timedelta
    query = session.query(mv_model.Deck).filter(mv_model.Deck.scrape_date.is_(None))
    print(query.count())
    for deck in query.all():
        deck.scrape_date = datetime.utcnow()-timedelta(days=287)
        session.add(deck)
    session.commit()

def fix_deck_card_counts():
    query = session.query(mv_model.DeckCard, mv_model.Deck)
    query = query.filter(mv_model.DeckCard.deck_key==mv_model.Deck.key,mv_model.DeckCard.card_key==mv_model.Card.key)
    print("start querying!")

    bulk_update = []
    bulk_update_size = 1000
    step = 10
    amt = 0
    last_date = '2020-06-01 00:07:16.758825'
    max_date = '2020-06-02 00:07:16.758825'
    deck_key = None
    while 1:
        #print("start while")
        next_batch = session.query(mv_model.Deck)
        next_batch = next_batch.order_by(mv_model.Deck.scrape_date)
        if last_date:
            #print("incorporate laste date")
            next_batch = next_batch.filter(mv_model.Deck.scrape_date>last_date)
        if max_date:
            next_batch = next_batch.filter(mv_model.Deck.scrape_date<max_date)
        if deck_key:
            next_batch = next_batch.filter(mv_model.Deck.key==deck_key)
        next_batch = next_batch.limit(step)
        #print(next_batch)
        print("access decks",last_date)
        time.sleep(0.02)
        next_batch = next_batch.all()
        if len(bulk_update) >= bulk_update_size or not next_batch:
            print("updating starting at ", deck.key, amt, deck.scrape_date, len(bulk_update))
            q = update(mv_model.DeckCard, bind=session).where(
                and_(mv_model.DeckCard.deck_key==bindparam('_deck_key'),
                mv_model.DeckCard.card_key==bindparam('_card_key'),
                mv_model.DeckCard.card_deck_expansion==bindparam('_card_deck_expansion'))
            ).values({'count': bindparam('count')})
            session.execute(q, bulk_update)
            session.commit()
            bulk_update[:] = []
            print("leftover:",len(bulk_update))
            amt += bulk_update_size
            print("update_complete")
        if not next_batch:
            break
        for deck in next_batch:
            last_date = deck.scrape_date
            for card_key in deck.get_unique_card_keys():
                if not deck.count(card_key):
                    crash
                bulk_update.append({
                "count": deck.count(card_key), 
                "_deck_key": deck.key, 
                "_card_key": card_key, 
                "_card_deck_expansion": deck.expansion})

