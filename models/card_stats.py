import os
import json
import collections

from sqlalchemy.sql.expression import bindparam
import __updir__
from models import wiki_card_db, mv_model, wiki_model
from sqlalchemy.sql import and_, not_, func, update, or_
from models import shared

session = mv_model.Session()

"""These are all the ways we need to unpack a card name:
    - (Evil Twin): look for Evil Twin rarity cards
    - (Anomaly): look for Anomaly version of the card
    - is_gigantic: probably don't need to do anything specific
    - multiple house: probably don't need to do anything specific (they can't maverick)"""

def query_card_versions(card_title, query):
    if "(Evil Twin)" in card_title:
        query = query.filter(and_(
            mv_model.Card.name==card_title.replace("(Evil Twin)","").strip(),
            mv_model.Card.data['rarity'].as_text()=='Evil Twin'
        ))
    elif "(Anomaly)" in card_title:
        query = query.filter(and_(
            mv_model.Card.name==card_title.replace("(Anomaly)","").strip(),
            mv_model.Card.data['is_anomaly'].as_boolean()
        ))
    else:
        query = query.filter(and_(
            mv_model.Card.name==card_title,
            not_(mv_model.Card.data['is_anomaly'].as_boolean())
        ))
    return query

def calc_mavericks(card_data):
    query = query_card_versions(card_data["card_title"], session.query(mv_model.Card))
    query = query.filter(mv_model.Card.data['is_maverick'].as_boolean()==True)
    houses = collections.defaultdict(lambda: set())
    for card in query.all():
        houses[card.deck_expansion].add(card.data['house'])
    return houses

def calc_legacy_maverick(card_data, expansions):
    query = query_card_versions(card_data["card_title"], session.query(mv_model.Card))
    query = query.filter(mv_model.Card.data['is_maverick'].as_boolean()==True)
    counts = collections.defaultdict(lambda: set())
    deck_ids = []
    for card in query.all():
        if card.deck_expansion not in expansions:
            print("counting", card.data)
            counts[card.deck_expansion].add(card.data['house'])
            for deckcount in session.query(mv_model.DeckCard).\
                filter(
                    mv_model.DeckCard.card_key==card.key,
                    mv_model.DeckCard.card_deck_expansion==card.deck_expansion).all():
                deck_ids.append(deckcount.deck_key)
    return {"houses":counts, "decks": deck_ids}

# Get count data from db first
count_data = {}
data_changed = set()
for count in session.query(mv_model.CardCounts).all():
    exp = int(count.deck_expansion)
    if count.name not in count_data:
        count_data[count.name] = {}
    if exp not in count_data[count.name]:
        count_data[count.name][exp] = {}
    dat = {}
    for key in count.data:
        dat[int(key)] = count.data[key]
    count_data[count.name][exp] = dat

def do_stats(deck):
    for card in deck.cards:
        renamed = wiki_model.rename_card_data(card.data)
        data_changed.add(renamed["card_title"])
        count_data[renamed["card_title"]] = dat = count_data.get(renamed["card_title"], {})
        count = int(deck.count(card.key))
        expansion = int(deck.expansion)
        if expansion not in dat:
            dat[expansion] = {}
        if count not in dat[expansion]:
            dat[expansion][count] = 0
        dat[expansion][count] += 1

if __name__ == "__main__":
    import time

    batch_size = 1000
    # Get starting page/index from DeckStatCounted
    stat_count = session.query(mv_model.DeckStatCounted)
    dsc = stat_count.first()
    if not dsc:
        dsc = mv_model.DeckStatCounted(start=0)
    while 1:
        print(f"batch starting with {dsc.start}")
        start = time.time()
        left_bound_page = dsc.start//int(24)
        left_bound_index = dsc.start-left_bound_page*24
        left_bound_page += 1
        print(left_bound_page, left_bound_index)
        q = session.query(mv_model.Deck).\
            filter(mv_model.Deck.page>=left_bound_page).\
            filter(or_(mv_model.Deck.page>left_bound_page,mv_model.Deck.index>=left_bound_index)).\
            order_by(mv_model.Deck.page, mv_model.Deck.index).\
            limit(batch_size)
        next_batch = q.all()
        if not next_batch:
            break
        print("going through batch")
        deck = next_batch[0]
        print(deck.key, deck.page, deck.index)
        for deck in next_batch:
            do_stats(deck)
        dsc.start = (deck.page-1)*24 + (deck.index) + 1
        print("adding", dsc, dsc.start)
        session.add(dsc)
        print("merge", data_changed)
        for name in data_changed:
            for expansion in count_data[name]:
                #print('merge', name, expansion, count_data[name][expansion])
                session.merge(mv_model.CardCounts(name=name, deck_expansion=expansion, data=count_data[name][expansion]))
        print('commmit')
        session.commit()
        data_changed.clear()
        duration = time.time()-start
        amt = float(batch_size)
        per_sec = amt/duration
        print(f'Batch finished. Rate={per_sec} Finish={((2201280-dsc.start)/per_sec)/60/60} hrs')
        start = time.time()

    print(count_data)


    # for card_name in sorted(wiki_card_db.cards):
    #     print(card_name)
    #     query = session.query(mv_model.Card)
    #     query = query_card_versions({"card_title":"Blood Money"}, query)
    #     counts = collections.defaultdict(lambda: 0)
    #     total_decks = 0
    #     for variant in query.execution_options(stream_results=True).yield_per(100):
    #         print("lookup variant", variant.key, variant.deck_expansion)
    #         countq = session.query(mv_model.DeckCard).filter(and_(
    #             mv_model.DeckCard.card_key==variant.key, 
    #             mv_model.DeckCard.card_deck_expansion==variant.deck_expansion))
    #         for count in countq.all():
    #             counts[int(count.count)] += 1
    #             total_decks += 1
    #             if total_decks % 1000 == 0:
    #                 time.sleep(0.02)
    #     session.merge(mv_model.CardCounts(name=card_name, data=counts))
    #     session.commit()
    #     time.sleep(1)
        
    # query = session.query(mv_model.DeckCard, mv_model.Card).filter(and_(
    #     mv_model.DeckCard.card_key==mv_model.Card.key, mv_model.DeckCard.card_deck_expansion==mv_model.Card.deck_expansion))
    # print("start querying!")
    # count = 0
    # offset = 0
    # step = 100
    # for deck_card in query.execution_options(stream_results=True).yield_per(step):
    #     count += 1
    #     if count == 1000000:
    #         break
    #     if count % 10000 == 0:
    #         time.sleep(0.02)
    print(time.time()-start)