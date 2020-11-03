from util import cargo_query
from wikibase import CargoTable
from mastervault import datamodel
import carddb


def get_event_results():
    search = {
        "tables": 'EventResults',
        "fields": "DeckID"
    }
    results = []
    for result in cargo_query(search)['cargoquery']:
        results.append(result['title']["DeckID"].strip())
    return [x.strip() for x in results if x.strip()]


def deck_to_cargo(key):
    session = datamodel.Session()
    deck = session.query(datamodel.Deck).filter(datamodel.Deck.key == key).first()
    if not deck:
        print("error looking up", key)
        return ""
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


def update_event_decks(wp):
    # Collect all event results
    eventresults = get_event_results()
    cargo_decks = {}
    for key in eventresults:
        cargo_decks[key] = deck_to_cargo(key)
    # Add deck cargo data to string
    out = "\n".join(cargo_decks.values())
    # Get EventDecks page
    p = wp.page("Deck:EventDecks")
    # Edit EventDecks page with string
    return p.edit(out, "Importing decks")