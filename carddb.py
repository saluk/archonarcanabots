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
        "453": "Worlds Collide",  # Put the anomalies in the same set
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

# TODO - as if it were yours, if you do, center of the battleline, preceding, instead and splash
replacement_links = {
    "ward": "Ward",
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
    "repeat": "Repeat",
    "repeats": "Repeat",
    "preceding": "Preceding",
    "preceding effect": "Preceding",
    "repeat the preceding effect": "Preceding",
    "purge": "Purge",
    "purged": "Purge",
    "graft": "Graft",
    "grafted": "Graft",
    "heal": "Heal",
    "flank": "Flank",
    "sacrifice": "Sacrifice",
    "put into play": "Put Into Play",
    "invulnerable": "Invulnerable",
    "pay": "Pay",
    "as if it were yours": "as if it were yours",
    "if you do": "if you do",
    "Center of your Battleline": "Center of the Battleline",
    "instead": "Replacement Effects",
    "forge a key": "Timing_Chart#Forge_a_Key",
    "current cost": "Cost",
    "cost": "Cost",
    "spent": "Forge",
    "spend": "Forge",
    "forging keys": "Forge",
    "take control": "Control",
    "control": "Control",
    "enhance": "Enhance",
    "for each": "For each"
    # TODO - ready and fight
}
for kw in keywords:
    replacement_links[kw.lower()] = kw.capitalize()
# TODO add linker for traits going to the category

remove_links = [
    "return",
    "archive",
    "archives"
]


def pull_keywords(text):
    found = []
    words = text.replace("\r", ". ").split(".")
    for w in words:
        for kw in keywords:
            if w.lower().strip().startswith(kw.lower()):
                found.append(kw)
                break
    return found


def modify_card_text(text, card_title, flavor_text=False):
    # Clean up carriage returns
    text = re.sub("(\r\n|\r|\x0b|\n)", "\r", text)
    # Clean up spaces
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


card_title_reg = []


blacklist_card_names = [
    "fear"
]


def link_card_titles(text, original_title):
    if not card_title_reg:
        card_titles = [x for x in get_card_titles() if not x.lower() in blacklist_card_names]
        card_titles = "|".join(card_titles).replace("(", r"\(").replace(")", r"\)")
        card_titles = re.sub('["””“]', ".", card_titles)
        card_title_reg.append(
            re.compile(r"(^|[^[a-z\-])("+card_titles+r")([^\]a-z]|$)", flags=re.IGNORECASE)
        )
    crazy_reg = card_title_reg[0]
    text = re.sub(crazy_reg, r"\1[[\2]]\3", text, count=1)
    text = re.sub(r"\[\[(%s)\]\]" % original_title, r"\1", text, flags=re.IGNORECASE)
    return text


def get_unidentified_characters():
    wp = connections.get_wiki()
    unidentified = wp.page("Category:Unidentified")
    return [p.title for p in unidentified.categorymembers()]


def linking_keywords(text):
    for kw in remove_links:
        text = re.sub(r"\[\[[^]]*?\|{0,1}("+kw+r")\]\]", r"\1", text, flags=re.IGNORECASE)
    for kw in sorted(replacement_links, key=lambda s: -len(s)):
        debracket = re.split(r"(\[\[.*?\]\])", text)
        rep = not debracket[0].startswith("[[")
        for i in range(len(debracket)):
            if rep:
                debracket[i] = re.sub(
                    r"(^|[^\|a-z])(%s)([^\|a-z]|$)" % kw, r"\1[[%s|\2]]\3" % replacement_links[kw],
                    debracket[i],
                    count=1,
                    flags=re.IGNORECASE
                )
            rep = not rep
        text = "".join(debracket)
    return text


t1 = "Elusive. (The first time this creature is attacked each turn, no damage is dealt.) <p> After a creature reaps, stun it."
t2 = "[[Elusive|Elusive]]. (The first time this creature is attacked each turn, no damage is dealt.) <p> After a creature reaps, stun it."
t3 = "[[Elusive|Elusive]]. (The first time this creature is attacked each turn, no damage is dealt.) <p> After a creature reaps, [[Stun|stun]] it."
assert linking_keywords(t1) == t3, linking_keywords(t1)
assert linking_keywords(t2) == t3, linking_keywords(t2)
assert linking_keywords(t3) == t3, linking_keywords(t3)
t4 = "[[Skirmish]]. (When you use this creature to fight, it is dealt no damage in [[return]].) <p> Fight: Draw a card. "
t5 = "[[Skirmish]]. (When you use this creature to fight, it is dealt no damage in return.) <p> Fight: Draw a card. "
assert (linking_keywords(t4)) == t5, linking_keywords(t4)
t6 = "'''Play:''' [[Return|Return]] an enemy creature to its owner’s hand."
t7 = "'''Play:''' Return an enemy creature to its owner’s hand."
assert (linking_keywords(t6)) == t7, linking_keywords(t6)
t8 = "'''Action:''' Purge a creature in play. If you do, your opponent gains control of Spangler Box. If Spangler Box leaves play, return to play all cards purged by Spangler Box."
t9 = "'''Action:''' [[Purge|Purge]] a creature in play. [[if you do|If you do]], your opponent gains [[Control|control]] of Spangler Box. If Spangler Box leaves play, return to play all cards [[Purge|purged]] by Spangler Box."
assert (linking_keywords(t8)) == t9, linking_keywords(t8)
t10 = "During your turn, if Captain Val Jericho is in the center of your battleline, you may play one card that is not of the active house."
t11 = "During your turn, if Captain Val Jericho is in the [[Center of the Battleline|center of your battleline]], you may play one card that is not of the active house."
assert (linking_keywords(t10)) == t11, linking_keywords(t10)
t12 = "After an enemy creature is destroyed while fighting, put a glory counter on The Colosseum. <p> '''Omni:''' If there are 6 or more glory counters on The Colosseum, remove 6 and forge a key at current cost."
t13 = "After an enemy creature is destroyed while fighting, put a glory counter on The Colosseum. <p> '''Omni:''' If there are 6 or more glory counters on The Colosseum, remove 6 and [[Timing_Chart#Forge_a_Key|forge a key]] at [[Cost|current cost]]."
assert (linking_keywords(t12)) == t13, linking_keywords(t12)
t14 = "'''Play:''' Discard the top card of your opponent’s deck and reveal their hand. You gain 1{{Aember}} for each card of the discarded card’s house revealed this way. Your opponent [[Repeat|repeat]]s the preceding effect on you."
t15 = "'''Play:''' Discard the top card of your opponent’s deck and reveal their hand. You gain 1{{Aember}} [[For each|for each]] card of the discarded card’s house revealed this way. Your opponent [[Repeat|repeat]]s the [[Preceding|preceding effect]] on you."
assert (linking_keywords(t14)) == t15, linking_keywords(t14)
t16 = "'''Play:''' Choose a creature. Deal 1{{Damage}} to it for each friendly creature. You may exalt a friendly creature to repeat the preceding effect."
t17 = "'''Play:''' Choose a creature. Deal 1{{Damage}} to it [[For each|for each]] friendly creature. You may [[Exalt|exalt]] a friendly creature to [[Preceding|repeat the preceding effect]]."
assert (linking_keywords(t16)) == t17, linking_keywords(t16)


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


def get_card_titles():
    return list(cards.keys()) + get_unidentified_characters()


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
    for card_title in cards:
        if only and card_title != only:
            continue
        card = get_latest(card_title)
        card["flavor_text"] = link_card_titles(card["flavor_text"], card_title)
        card["card_text"] = link_card_titles(card["card_text"], card_title)
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


def get_cargo(card, ct):
    latest = get_latest_from_card(card)
    cardtable = {
        "Name": latest["card_title"] or crash,
        "Image": latest["front_image"] or crash,
        "Artist": "",
        "Text": latest["card_text"] or "",
        "Keywords": " • ".join(latest["keywords"]),
        "FlavorText": latest["flavor_text"] or "",
        "Power": latest["power"] or "",
        "Armor": latest["armor"] or "",
        "Amber": latest["amber"] or "",
        "Type": latest["card_type"] or crash,
        "House": latest["house"] or "",
        "Traits": latest["traits"] or "",
        "Rarity": latest["rarity"] or crash
    }
    ct.update_or_create("CardData", latest["card_title"], cardtable)
    for (set_name, set_num, card_num) in get_sets(card):
        settable = {
            "SetName": set_name,
            "SetNumber": set_num,
            "CardNumber": card_num
        }
        ct.update_or_create("SetData", set_name, settable)


def all_traits():
    traits = set()
    for card in cards:
        ct = get_latest(card)["traits"]
        if ct:
            for tt in ct.split(" • "):
                traits.add(tt)
    return sorted(traits)



if __name__ == "__main__":
    load_json()
    print(link_card_titles("something Orb of Wonder", "Lesser Oxtet"))
    print(link_card_titles("something Orb of Wonder and Lesser Oxtet.", "Lesser Oxtet"))
    print(link_card_titles("controller", "something"))
    print(link_card_titles("So, this nonlethal [[containment field]]; how lethal do you want it?", "Containment Field"))
    print(link_card_titles("“When you have eliminated the imp-ossible, whatever remains, however imp-robable, must be the truth.” – Quixo the ”Adventurer”", "Not Quixo"))
    print(link_card_titles("'''Action:''' Fully [[Heal|heal]] an Ancient Bear. If there are no Ancient Bears in play, [[Search|search]] your deck and discard pile and put each Ancient Bear from them into your hand. [[if you do|If you do]], shuffle your discard pile into your deck.", "Not Quixo"))
    #load_from_mv_files()
    print(repr(all_traits()))
else:
    load_json()

#assert(get_latest("A Fair Game")["expansion"] == 452), get_latest("A Fair Game")["expansion"]