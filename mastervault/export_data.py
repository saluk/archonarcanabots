import datamodel
import json
import time
from sqlalchemy import Integer, or_, text
session = datamodel.Session()

OUT_FILE = 'mastervault/static/win_rates.csv'
OUT_FILE_CT = 'mastervault/static/win_rates_tracker.csv'
CRUCIBLE_TRACKER_IN_FILE = '/mnt/opt/saluk/crucible-tracker/win_rates.json'


indexer = {}
houses = []
expansions = []
expansion_card_number = {}


def populate_data():
    i = 0

    print("gen house indexes")
    houses.extend([
        x[0] for x in session.execute(text("select distinct(data->>'house') from cards;"))
    ])
    for h in sorted(houses):
        indexer[h] = i
        i += 1

    print("collect expansions")
    expansions.extend([
        int(x[0]) for x in session.execute(text("select distinct(data->>'expansion') from cards;"))
    ])

    print("collect card numbers")
    for exp in sorted(expansions):
        expansion_card_number[exp] = []
        print("gen expansion, card number for expansion {0}".format(exp))
        expansion_card_number[exp].extend([
            str(x[0]) for x in session.execute(text(
                "select distinct(data->>'card_number') from cards where data->>'expansion'='{0}';".format(exp)
            ))
        ])
        for card_num in sorted(expansion_card_number[exp]):
            if(str(exp) == '341' and card_num == '001'):
                print(i)
            indexer[(str(exp), str(card_num))] = i
            i += 1
    indexer["total_features"] = i
    print("anger should be:", 9, "and is:", indexer[('341', '001')])


populate_data()


def has_played_op(query):
    return query.filter(or_(
        datamodel.Deck.data['wins'].astext.cast(Integer) > 0,
        datamodel.Deck.data['losses'].astext.cast(Integer) > 0
    ))


def embeddable_feature_ids(deck):
    """For embeddings"""
    compressed_list = []
    for house in deck.data['_links']['houses']:
        compressed_list.append(str(indexer[house]))
    keys = []
    for card in deck.get_cards():
        compressed_list.append(
            str(indexer[
                (str(card.data['expansion']), str(card.data['card_number']))
            ])
        )
        keys.append(card.key)
    assert len(compressed_list) == 36+3, (len(compressed_list), deck.key)
    return " ".join(compressed_list)


def bag_of_words(deck):
    features = [0] * indexer["total_features"]
    for house in deck.data['_links']['houses']:
        index = indexer[house]
        features[index] += 1
    for card in deck.get_cards():
        index = indexer[
                (str(card.data['expansion']), str(card.data['card_number']))
        ]
        features[index] += 1
    assert sum(features) == 39
    s = " ".join([str(x) for x in features])
    return s


def winrate(wins, losses):
    return float(wins) / (
        float(losses) + float(wins)
    )


def output_win_rates(short=False):
    r = session.execute(text("select max(page) from decks"))
    count = list(r)[0][0]
    with open(OUT_FILE, 'w') as f:
        for page in range(count):
            print("{0}/{1}".format(page, count))
            for deck in has_played_op(session.query(datamodel.Deck)).filter(datamodel.Deck.page == page):
                print("  {0}".format(deck.key))
                f.write("{0} {1} {2}\n".format(
                    deck.key, bag_of_words(deck), winrate(deck.data['wins'], deck.data['losses'])
                ))
                if short:
                    return


def output_tracker_rates(short=False):
    s = time.time()
    with open(CRUCIBLE_TRACKER_IN_FILE) as f:
        decks = json.loads(f.read())
    keybatch_size = 100
    for i in range(0, len(decks.keys()), keybatch_size):
        print(i/keybatch_size, len(decks.keys())/keybatch_size)
        for deck in session.query(datamodel.Deck).filter(
            datamodel.Deck.key.in_(
                list(decks.keys())[i:i+keybatch_size]
            )
        ):
            decks[deck.key]['encoding'] = bag_of_words(deck)
        if short:
            break
    print("time:", keybatch_size, time.time()-s)
    highest_games = 0
    highest_key = None
    total_games = 0
    total_decks = len(decks.keys())
    with open(OUT_FILE_CT, 'w') as f:
        for key, deck in decks.items():
            if "encoding" not in deck:
                continue
            game_count = deck['wins'] + deck['losses']
            total_games += game_count
            if game_count > highest_games:
                highest_games = game_count
                highest_key = key
            f.write('{0} {1} {2}\n'.format(
                key, deck['encoding'], winrate(deck['wins'], deck['losses'])
            ))
    print('average games per deck:{0}'.format(float(total_games)/float(total_decks)))
    print('most games:{0} from {0}'.format(highest_games, highest_key))
    print('all games:', total_games)


#output_win_rates()
output_tracker_rates()