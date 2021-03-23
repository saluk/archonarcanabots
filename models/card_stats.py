import os
import json
import time
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

def expansion_totals():
    exp_totals = {}
    counts = session.query(mv_model.Counts).filter(mv_model.Counts.label.like('total_%')).all()
    for c in counts:
        if c.label == 'total_deck_count':
            continue
        exp = c.label.rsplit('_', 1)[1]
        exp_totals[int(exp)] = c.count
    return exp_totals


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

def do_card_counts(deck):
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

def commit_card_counts():
    print("merge", data_changed)
    for name in data_changed:
        for expansion in count_data[name]:
            #print('merge', name, expansion, count_data[name][expansion])
            session.merge(mv_model.CardCounts(name=name, deck_expansion=expansion, data=count_data[name][expansion]))
    print('commmit')
    data_changed.clear()

house_counts = {}
for count in session.query(mv_model.HouseCounts).all():
    exp = int(count.deck_expansion)
    if exp not in house_counts:
        house_counts[exp] = {}
    house_counts[exp][count.name] = count.count
    
def do_house_counts(deck):
    if deck.expansion not in house_counts:
        house_counts[deck.expansion] = {}
    for house in deck.get_houses():
        if house not in house_counts[deck.expansion]:
            house_counts[deck.expansion][house] = 0
        house_counts[deck.expansion][house] += 1

def commit_house_counts():
    for exp,v in house_counts.items():
        for house, count in v.items():
            session.merge(mv_model.HouseCounts(name=house, deck_expansion=exp, count=count))

def count_decks(label, stat_func, commit_func):
    batch_size = 1000
    # Get starting page/index from DeckStatCounted
    stat_count = session.query(mv_model.DeckStatCounted).filter(mv_model.DeckStatCounted.label==label)
    dsc = stat_count.first()
    if not dsc:
        dsc = mv_model.DeckStatCounted(label=label, start=0)
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
            stat_func(deck)
        dsc.start = (deck.page-1)*24 + (deck.index) + 1
        print("adding", dsc, dsc.start)
        session.add(dsc)
        commit_func()
        session.commit()
        duration = time.time()-start
        amt = float(batch_size)
        per_sec = amt/duration
        print(f'Batch finished. Rate={per_sec} Finish={((2201280-dsc.start)/per_sec)/60/60} hrs')
        start = time.time()

    print(count_data)
    print(time.time()-start)

if __name__ == "__main__":
    #count_decks('card_counts', do_card_counts, commit_card_counts)
    count_decks('house_counts', do_house_counts, commit_house_counts)