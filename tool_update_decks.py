import collections
from operator import add
from util import cargo_query
from wikibase import CargoTable
from mastervault import datamodel
import carddb


def get_event_results():
    search = {
        "tables": 'EventResults',
        "fields": "DeckID, Name"
    }
    results = []
    for result in cargo_query(search)['cargoquery']:
        r = {
            "DeckID": result['title']["DeckID"].strip(),
            "Name": result['title']['Name'].strip()
        }
        if not r["DeckID"]:
            continue
        results.append(r)
    return results


def deck_to_cargo(deck):
    cards = list(deck.get_cards())
    fields = {
        "DeckName": deck.name,
        "DeckID": deck.key,
        "Houses": "•".join([""] + deck.houses + [""]),
        "SetName": carddb.nice_set_name(deck.expansion),
        "UpgradeCount": len([c for c in cards if c.card_type == "Upgrade"]),
        "CreatureCount": len([c for c in cards if c.card_type in ["Creature", "Creature1"]]),
        "ArtifactCount": len([c for c in cards if c.card_type == "Artifact"]),
        "ActionCount": len([c for c in cards if c.card_type == "Action"])
    }
    ct = CargoTable()
    ct.update_or_create('EventDeck', 'EventDeck', fields)
    return ct.output_text()


def card_to_cargo(store_card):
    ct = CargoTable()
    ct.update_or_create("EventCardStats", "EventCardStats", store_card)
    return ct.output_text()


def update_event_decks(wp):
    # Collect all event results
    eventresults = get_event_results()
    cargo_decks = {}
    events = collections.defaultdict(lambda: [])
    
    session = datamodel.Session()
    for result in eventresults:
        deck = session.query(datamodel.Deck).filter(datamodel.Deck.key == result["DeckID"]).first()
        if not deck:
            print("error looking up", key)
            continue
        cargo_decks[result["DeckID"]] = deck_to_cargo(deck)
        events[result["Name"]].append(deck)

    updates = []
    for event_name in events:
        cards = collections.defaultdict(lambda: {
            "EventName": "",
            "CardName": "",
            "Rarity": "",
            "Type": "",
            "Total": 0,
            "Decks": 0
        })
        for deck in events[event_name]:
            added_to_deck = set()
            for card in deck.get_cards():
                card = card.aa_format()
                store = cards[(card["card_title"], event_name)]
                store.update({
                    "EventName": event_name,
                    "CardName": card["card_title"],
                    "Rarity": card["rarity"],
                    "Type": card["card_type"]
                })
                store["Total"] += 1
                if not card["card_title"] in added_to_deck:
                    store["Decks"] += 1
                    added_to_deck.add(card["card_title"])
        p = wp.page("Deck:EventCardStats_"+event_name.replace(" ", "_"))
        up = p.edit(
            "\n".join([
                card_to_cargo(card) for card in cards.values()
            ]),
            "Importing Event Card Stats"
        )
        updates.append(up)
        print(up)

    # Add deck cargo data to string
    out = "\n".join(cargo_decks.values())
    # Get EventDecks page
    p = wp.page("Deck:EventDecks")
    # Edit EventDecks page with string
    up = p.edit(out, "Importing decks")
    updates.append(up)
    print(up)
    return updates