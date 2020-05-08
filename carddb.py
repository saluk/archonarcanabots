import os
import json
import re
from fuzzywuzzy import fuzz
from html_sanitizer import Sanitizer
import connections

sanitizer = Sanitizer()

cards = {}

SETS = {452: "WC", 453: "WC-A", 341: "CotA", 435: "AoA"}
SET_BY_NUMBER = {}
SET_ORDER = []
for numerical_set in sorted(SETS.keys()):
    setname = SETS[numerical_set]
    SET_ORDER.append(setname)
    SET_BY_NUMBER[setname] = numerical_set


def nice_set_name(num):
    return {
        "452": "Worlds Collide",
        "453": "Worlds Collide",  #Put the anomalies in the same set
        "341": "Call of the Archons",
        "435": "Age of Ascension"
    }[str(num)]


def sanitize_name(name):
    return sanitizer.sanitize(name.replace("[", "(").replace("]", ")"))

# TODO pull this direct from the site
keywords = """Alpha
Assault
Deploy
Elusive
Hazardous
Invulnerable
Omega
Poison
Skirmish
Taunt""".split("\n")

replacement_links = {
    "ward": "Ward",
    "archive": "Archives",
    "enrage": "Enrage",
    "exalt": "Exalt",
    "pay": "Pay",
    "move": "Move",
    "unforge": "Unforge",
    "tide": "Tide",
    "swap": "Swap",
    "stun": "Stun",
    "splash": "Splash",
    "search": "Search",
    "return": "Return",
    "repeat": "Repeat",
    "purge": "Purge",
    "graft": "Graft",
    "heal": "Heal",
    "flank": "Flank"
}


def pull_keywords(text):
    found = []
    words = text.replace("\r",". ").split(".")
    for w in words:
        for kw in keywords:
            if w.lower().strip().startswith(kw.lower()):
                found.append(kw)
                break
    return found


def modify_card_text(text, card_title, flavor_text=False):
    #Clean up carriage returns
    text = re.sub("(\r\n|\r|\x0b|\n)", "\r", text)
    #Clean up spaces
    text = re.sub("\u202f", " ", text)

    # If there is an "A" at the begining of a sentance, replace it
    # Po's Pixies has an aember symbol at the begining of a sentance
    if card_title not in ["Po’s Pixies", "Sack of Coins"]:
        text = re.sub(r"(^|: |\. |\r)A", r"\1$A$", text)

    # Turn <A> or something A or 1A or +A or -A into {{Aember}} or {{Aember}} or 1{{Aember}}
    text = re.sub(r"( |\+|\-|–|\r)(\d+)*\<{0,1}A\>{0,1}( |$|\.|\,)", r"\1\2{{Aember}}\3", text)
    text = re.sub(r"( |\+|\-|–|\r)(\d+)*\<{0,1}D\>{0,1}( |$|\.|\,)", r"\1\2{{Damage}}\3", text)

    # Replace A's at the begining of the sentance again
    text = re.sub(r"\$A\$", "A", text)

    if not flavor_text:
        # bold abilities at the begining of a line or following a new line
        text = re.sub(r"(^|\r|“|‘)((\w|\/| )+\:)", r"\1'''\2'''", text)

    text = re.sub(r"(\u000b|\r)", " <p> ", text)

    # Replace trailing <p> and spaces
    text = re.sub(r"(<p>| )+$", "", text)
    return text


def linking_keywords(text):
    for kw in keywords:
        text = re.sub("(^|[^[])"+kw+"([^]]|$)", r"\1[["+kw.capitalize()+r"]]\2", text)
    # TODO - we may pull these somewhere else
    """for glossary in replacement_links:
        text = re.sub(
            "(^|[^[])("+glossary+")([^]]|$)", r"\1[[%s|\2]]\3" % replacement_links[glossary],
            text,
            flags=re.IGNORECASE
        )"""
    return text


def safe_name(name):
    # if name == "Ortannu’s Binding" or name == "Nature’s Call":
    #    return name.replace("’", "'")
    return name


def nice_rarity(rarity):
    if rarity == "FIXED":
        return "Fixed"
    return rarity


def image_number(card):
    return "%s-%s.png" % (card["expansion"], card["card_number"])


def get_sets(card):
    for set_num in sorted(SETS.keys()):
        if str(set_num) in card:
            yield (nice_set_name(set_num), set_num, card[str(set_num)]["card_number"])


def get_latest_from_card(card):
    for (set_name, set_num, card_num) in reversed(list(get_sets(card))):
        return card[str(set_num)]
    raise Exception("couldn't find a set in", card)


def add_card(card):
    title = sanitize_name(card["card_title"])
    title = safe_name(title)
    card["card_title"] = title
    card["keywords"] = pull_keywords(card["card_text"])
    card["card_text"] = linking_keywords(modify_card_text(card["card_text"] or "", title))
    card["flavor_text"] = modify_card_text(card["flavor_text"] or "", title, flavor_text=True)
    card["front_image"] = image_number(card)
    card["rarity"] = nice_rarity(card["rarity"])
    if card.get("is_anomaly", False):
        card["house"] = "Anomaly"

    if title not in cards:
        cards[title] = {}

    cards[title][str(card["expansion"])] = card


def fuzzyfind(name, threshold=80):
    s = sanitize_name(name)
    matches = []
    for lookup_name in cards.keys():
        r = fuzz.ratio(s.lower(), lookup_name.lower())
        if r > threshold:
            matches.append((lookup_name, r))
    if not matches:
        return None
    matches.sort(key=lambda i: i[1])
    return matches[-1][0]


def link_card_titles(text, original_title, card_titles):
    card_titles = "|".join([x for x in card_titles if x!=original_title]).replace("(", r"\(").replace(")", r"\)")
    crazy_reg = r"(^|[^[])("+card_titles+r")([^]]|$)"
    text = re.sub(crazy_reg, r"\1[[\2]]\3", text)
    return text


def get_unidentified_characters():
    wp = connections.get_wiki()
    unidentified = wp.page("Category:Unidentified")
    return [p.title for p in unidentified.categorymembers()]


def load_from_mv_files(only=None):
    cards.clear()
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
    card_titles = list(cards.keys()) + get_unidentified_characters()
    for card_title in cards:
        if only and card_title != only:
            continue
        card = get_latest(card_title)
        card["flavor_text"] = link_card_titles(card["flavor_text"], card_title, card_titles)
        card["card_text"] = link_card_titles(card["card_text"], card_title, card_titles)
    with open("my_card_db.json", "w") as f:
        f.write(json.dumps(cards, indent=2, sort_keys=True))
    print("saved.")


def load_json():
    cards.clear()
    with open("my_card_db.json") as f:
        cards.update(json.loads(f.read()))


def get_latest(card_title, fuzzy=False):
    if fuzzy:
        card_title = fuzzyfind(card_title)
    card = get_latest_from_card(cards[card_title])
    return card


if __name__ == "__main__":
    load_from_mv_files()
else:
    load_json()

assert(get_latest("A Fair Game")["expansion"] == 452), get_latest("A Fair Game")["expansion"]