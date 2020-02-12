import os
import json
from fuzzywuzzy import fuzz
from html_sanitizer import Sanitizer

sanitizer = Sanitizer()

cards = {}

def sanitize_name(name):
    return sanitizer.sanitize(name.replace("[", "(").replace("]", ")"))

def collect_latest_card(card_name):
    card_name = sanitize_name(card_name)
    card_d = cards[card_name]
    d = {}
    expansions = []
    for set_instance in card_d.values():
        expansions.append(
            (SETS[set_instance["expansion"]],
             set_instance["card_number"])
        )
    for e in sorted(card_d.keys()):
        d.update(card_d[e])
    d["sets"] = expansions
    return d

def add_card(card):
    title = sanitize_name(card["card_title"])
    card["card_title"] = title
    if title not in cards:
        cards[title] = {}
    cards[title][int(card["expansion"])] = card


def fuzzyfind(name, threshold=80):
    s = sanitize_name(name)
    matches = []
    for lookup_name in cards.keys():
        r = fuzz.ratio(s.lower(),lookup_name.lower())
        if r>threshold:
            matches.append((lookup_name, r))
    if not matches:
        return None
    matches.sort(key=lambda i: i[1])
    return matches[-1][0]

# sort it so that we get the newest data last
for card_file in os.listdir("skyjedi"):
    with open("skyjedi/" + card_file) as f:
        card_name_index = {}
        this_set_cards = json.loads(f.read())
        for card in this_set_cards:
            title = card["card_title"].strip()
            card["card_title"] = title
            if title in card_name_index:
                print("DUPLICATE:", card["card_title"])
            card_name_index[title] = card
            add_card(card)

if __name__=="__main__":
    print(fuzzyfind("chuff ape"))
    print(fuzzyfind("mega Ganger Cheiftain"))
    print(fuzzyfind("REDACTED"))
    print(fuzzyfind("Shard of Life"))
