import os
import json
import re
from fuzzywuzzy import fuzz
from html_sanitizer import Sanitizer
import connections
import util
from util import SEPARATOR
from mastervault import datamodel
import csv

sanitizer = Sanitizer()

cards = {}

SETS = {452: "WC", 
        453: "WC-A", 
        341: "CotA", 
        435: "AoA", 
        479: "MM"}
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
        "435": "Age of Ascension",
        "479": "Mass Mutation"
    }[str(num)]


hard_code = {
    "Exchange Officer": {
        "update": {
            "house": "Star Alliance"
        }
    },
    "Orb of Wonder": {
        "rename_expansion": {
            453: "%s (Anomaly)"
        }
    }
}


def sanitize_name(name):
    name = sanitizer.sanitize(name.replace("[", "(").replace("]", ")"))
    name = util.dequote(name)
    return name

def sanitize_trait(trait):
    return trait.replace("[","").replace("]","")

def sanitize_text(text, flavor=False):
    t = re.sub("(?<!\.)\.\.{1}$", ".", text)
    t = t.replace("\ufeff", "")
    t = t.replace("\u202f", " ")
    if flavor:
        t = re.sub(" *(\n|\r\n) *", " ", t)
    return t

assert sanitize_text("blah.") == "blah.", sanitize_text("blah.")
assert sanitize_text("blah..") == "blah.", repr(sanitize_text("blah.."))
assert sanitize_text("blah") == "blah"
assert sanitize_text("blah... something") == "blah... something"
assert sanitize_text("blah...") == "blah...", sanitize_text("blah...")
assert sanitize_text("'''Play:''' Deal 4{{Damage}} to a creature that is not on a [[Flank|flank]], with 2{{Damage}} [[Splash|splash]].\ufeff\ufeff") == "'''Play:''' Deal 4{{Damage}} to a creature that is not on a [[Flank|flank]], with 2{{Damage}} [[Splash|splash]]."
assert sanitize_text("\u201cThe Red Shroud will defend the Crucible\r\nfrom the threat of dark \u00e6mber.\u201d", flavor=True) == "\u201cThe Red Shroud will defend the Crucible from the threat of dark \u00e6mber.\u201d", repr(sanitize_text("\u201cThe Red Shroud will defend the Crucible\r\nfrom the threat of dark \u00e6mber.\u201d", flavor=True))
assert sanitize_text("something    \n    something else", flavor=True)=="something something else"



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
    "for each": "For each"
    # TODO - ready and fight
}
for kw in keywords:
    replacement_links[kw.lower()] = kw.capitalize()

remove_links = [
    "return",
    "archive",
    "archives"
]


def get_keywords_text(text):
    """Return a list of keywords found on the card (ignore keyword values like the '2' in 'Assault 2')"""
    found = []
    words = text.replace("\r", ". ").split(".")
    for w in words:
        for kw in keywords:
            if w.lower().strip().startswith(kw.lower()):
                found.append(kw)
                break
    return found


def get_keywordvalue_text(text, kw):
    """Returns the value of a specific keyword, like the '2' in 'Assault 2'"""
    found = re.findall(r'%s *(\d+|x)' % kw, text, re.IGNORECASE)
    if found:
        return found[0]
    return ""


def read_enhanced(text):
    # Enhancements
    enhanced = re.match("(Enhance (A*)((PT)*)(D*)(R*))", text)
    ea=ept=ed=er=0
    if enhanced:
        ea = enhanced.group(2).count("A")
        a = "{{Aember}}" * ea
        ept = enhanced.group(3).count("PT")
        pt = "{{Capture}}" * ept
        ed = enhanced.group(5).count("D")
        d = "{{Damage}}" * ed
        er = enhanced.group(6).count("R")
        r = "{{Draw}}" * er
        text = text[:enhanced.start()] + "[[Enhance]] " + "".join([a, pt, d, r]) + text[enhanced.end():]
    return text, {'enhance_amber':ea, 'enhance_capture':ept, 'enhance_damage':ed, 'enhance_draw':er}


def modify_card_text(text, card_title, flavor_text=False):
    # Clean up carriage returns
    text = re.sub("(\r\n|\r|\x0b|\n)", "\r", text)
    # Clean up spaces
    text = re.sub("\u202f", " ", text)

    # If there is an "A" at the begining of a sentance, don't replace it
    # Po's Pixies has an aember symbol at the begining of a sentance
    if card_title not in ["Po’s Pixies", "Sack of Coins"]:
        text = re.sub(r"(^|: |\. |\r)A", r"\1$A$", text)

    # Turn <A> or something A or 1A or +A or -A into {{Aember}} or {{Aember}} or 1{{Aember}}
    text = re.sub(r"( |\+|\-|–|\r)(\d+)*\<{0,1}A\>{0,1}( |$|\.|\,)", r"\1\2{{Aember}}\3", text)
    text = re.sub(r"( |\+|\-|–|\r)(\d+)*\<{0,1}D\>{0,1}( |$|\.|\,)", r"\1\2{{Damage}}\3", text)
    # Bonus icon PT's and R's
    text = re.sub(r"( |\+|\-|–|\r)(\d+)*\<{0,1}PT\>{0,1}( |$|\.|\,)", r"\1\2{{Capture}}\3", text)
    text = re.sub(r"( |\+|\-|–|\r)(\d+)*\<{0,1}R\>{0,1}( |$|\.|\,)", r"\1\2{{Draw}}\3", text)

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
trait_reg = []


blacklist_card_names = [
    "fear"
]

def card_titles_that_link():
    return [x for x in get_card_titles() if not x.lower() in blacklist_card_names]


def link_card_titles(text, original_title):
    if not card_title_reg:
        card_titles = sorted([x for x in card_titles_that_link() if not x.lower() in blacklist_card_names])
        card_titles = "|".join(card_titles).replace("(", r"\(").replace(")", r"\)")
        card_titles = re.sub('["””“]', ".", card_titles)
        r = r"(^|[^[a-z\-])("+card_titles+r")([^\]a-z]|$)"
        card_title_reg.append(
            re.compile(r, flags=re.IGNORECASE)
        )
    crazy_reg = card_title_reg[0]
    # Replace card titles with link
    text = re.sub(crazy_reg, r"\1[[STITLE\2ETITLE]]\3", text)
    # Replace remaining matches with STITLE/ETITLE tags
    text = re.sub(crazy_reg, r"\1STITLE\2ETITLE\3", text)
    # Replace self-referential card title with no link
    text = re.sub(r"\[\[STITLE(%s)ETITLE\]\]" % original_title, r"STITLE\1ETITLE", text, flags=re.IGNORECASE)
    if "Quixo" in text:
        print(text)
    return text

traits_blacklist = [
    "power"
]
def link_card_traits(card, preload_traits=[]):
    """Must be run after link_card_titles"""
    if not trait_reg or preload_traits:
        trait_reg.clear()
        if not preload_traits:
            preload_traits = all_traits()
        card_traits = [t.lower() for t in preload_traits]
        # ignore traits in the blacklist as well as traits that are in card titles
        card_traits = [t for t in card_traits if t not in traits_blacklist]
        card_traits = "|".join(card_traits).replace("(", r"\(").replace(")", r"\)")
        card_traits = re.sub('["””“]', ".", card_traits)
        print(r"(^|[^[a-z\-])("+card_traits+r")([^\]a-z]|$)")
        trait_reg.append(
            re.compile(r"(^|[^[a-z\-])("+card_traits+r")([^\]a-z]|$)", flags=re.IGNORECASE)
        )
    bits = []
    if re.findall("(STITLE|ETITLE)", card["card_text"]):
        index = 0
        for match in re.finditer("(STITLE|ETITLE)", card["card_text"]):
            left = card["card_text"][index:match.start(1)]
            index = match.end()
            #right = card["card_text"][match.end(1):]
            bits.append(left)
            bits.append(card["card_text"][match.start(1):match.end(1)])
            #bits.append(card["card_text"][match.start():match.end()])
        bits.append(card["card_text"][match.end(1):])
    else:
        bits = [card["card_text"]]
    #print(repr(bits))
    #Only do replacements in bits of text that are NOT within STITLE and ETITLE
    allowed = True
    for i in range(len(bits)):
        if bits[i]=="STITLE":
            allowed = False
            continue
        elif bits[i]=="ETITLE":
            allowed = True
            continue
        if allowed:
            #print("is allowed")
            #print(re.findall(trait_reg[0], bits[i]), bits[i])
            bits[i] = re.sub(trait_reg[0], r'\1[http://archonarcana.com/Card_Gallery?traits=\2 \2]\3', bits[i])
    card["card_text"] = "".join(bits)
    return card["card_text"]

t1 = "After a Mutant creature enters STITLE A Dark Mutant Or Something ETITLE play, enrage Berinon. Reap: Capture 2A."
t2 = "After a [http://archonarcana.com/Card_Gallery?traits=Mutant Mutant] creature enters STITLE A Dark Mutant Or Something ETITLE play, enrage Berinon. Reap: Capture 2A."
card = {"card_text": t1}
t3 = link_card_traits(card, preload_traits=["Mutant"]) 
assert t3 == t2, t3

t1 = "After a Mutant creature enters play, [[Enrage|enrage]] STITLEBerinonETITLE.  <p> '''Reap:''' Capture 2{{Aember}}."
t2 = "After a [http://archonarcana.com/Card_Gallery?traits=Mutant Mutant] creature enters play, [[Enrage|enrage]] STITLEBerinonETITLE.  <p> '''Reap:''' Capture 2{{Aember}}."
card = {"card_text": t1}
t3 = link_card_traits(card, preload_traits=["Mutant"]) 
assert t3 == t2, t3

t1 = "'''Play:''' Ready each friendly Knight creature."
t2 = "'''Play:''' Ready each friendly [http://archonarcana.com/Card_Gallery?traits=Knight Knight] creature."
card = {"card_text": t1}
t3 = link_card_traits(card, preload_traits=["Knight"]) 
assert t3 == t2, t3
trait_reg.clear()


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
    ot = card["card_title"]
    if ot in hard_code:
        commands = hard_code[ot]
        card.update(commands.get("update", {}))
        for exp in commands.get("rename_expansion", {}):
            if exp != card["expansion"]:
                continue
            new_name = commands["rename_expansion"][exp]
            new_name = new_name.replace("%s", ot)
            card["card_title"] = new_name

    title = sanitize_name(card["card_title"])
    title = safe_name(title)
    card["card_title"] = title
    card["keywords"] = get_keywords_text(card["card_text"])
    card.update({"assault": "", "hazardous": "",
                 "enhance_amber": "", "enhance_damage": "",
                 "enhance_capture": "", "enhance_draw": ""})
    if card["card_type"] in ["Creature1", "Creature2"]:
        card["card_type"] = "Creature"
        card["subtype"] = "Gigantic"
    if card["card_type"] == "Creature":
        card["assault"] = get_keywordvalue_text(card["card_text"], "assault") or 0
        card["hazardous"] = get_keywordvalue_text(card["card_text"], "hazardous") or 0
        card["power"] = card["power"] or 0
        card["armor"] = card["armor"] or 0
    else:
        if card["power"] and not int(card["power"]):
            card["power"] = ""
        if card["armor"] and not int(card["armor"]):
            card["armor"] = ""

    card["card_text"] = sanitize_text(card["card_text"] or "")
    card["flavor_text"] = sanitize_text(card["flavor_text"] or "", flavor=True)

    card["card_text_search"] = card["card_text"]
    card["flavor_text_search"] = card["flavor_text"]

    card["card_text"], enhancements = read_enhanced(card["card_text"])
    card.update(enhancements)

    card["card_text"] = linking_keywords(modify_card_text(card["card_text"], title))
    card["flavor_text"] = modify_card_text(sanitize_text(card["flavor_text"]), title, flavor_text=True)

    card["image_number"] = image_number(card)
    card["rarity"] = nice_rarity(card["rarity"])
    if card.get("is_anomaly", False):
        card["house"] = "Anomaly"
    if card["traits"]:
        card["traits"] = SEPARATOR.join([sanitize_trait(t) for t in card["traits"].split(SEPARATOR)])

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


def get_card_by_number(num, expansion):
    num_index = {}
    for card in cards:
        for setid in cards[card]:
            card_in_set = cards[card][setid]
            num_index[(card_in_set["card_number"], setid)] = cards[card]
    if type(num)==type(1):
        num = ("000"+str(num))[-3:]
    return num_index[(num, str(expansion))]


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

    scope = datamodel.UpdateScope()
    for set_id in [479]:
        for card in scope.get_cards(set_id):
            add_card(card.data)
    for card_title in cards:
        if only and card_title != only:
            continue
        card = get_latest(card_title)
        card["flavor_text"] = link_card_titles(card["flavor_text"], card_title) #leaves behind stitle/etitle tags
        card["card_text"] = link_card_titles(card["card_text"], card_title)  #leaves behind stitle/etitle tags
        link_card_traits(card)  #uses stitle/etitle tags to avoid covering the same ground
        #Clean up stitle/etitle tags
        card["card_text"] = re.sub("(STITLE|ETITLE)", "", card["card_text"])
        card["flavor_text"] = re.sub("(STITLE|ETITLE)", "", card["flavor_text"])

    with open('data/artists_479.csv') as f:
        header = False
        for line in csv.reader(f):
            if not header:
                header = True
                continue
            num, artist = line
            card = get_card_by_number(int(num), 479)
            get_latest_from_card(card)["artist"] = artist

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


def get_cargo(card, ct=None, restricted=[], only_sets=False):
    if not ct:
        from wikibase import CargoTable
        ct = CargoTable()
    latest = get_latest_from_card(card)
    cardtable = {
        "Name": latest["card_title"],
        "Image": latest["image_number"],
        "Artist": latest.get("artist", ""),
        "Text": latest["card_text"],
        "Keywords": SEPARATOR.join(latest["keywords"]),
        "FlavorText": latest["flavor_text"],
        "Power": latest["power"],
        "Armor": latest["armor"],
        "Amber": latest["amber"],
        "Assault": latest["assault"],
        "Hazardous": latest["hazardous"],
        "EnhanceDamage": latest["enhance_damage"],
        "EnhanceAmber": latest["enhance_amber"],
        "EnhanceDraw": latest["enhance_draw"],
        "EnhanceCapture": latest["enhance_capture"],
        "Type": latest["card_type"],
        "House": latest["house"],
        "Traits": latest["traits"],
        "Rarity": latest["rarity"]
    }
    assert "Artist" not in restricted
    if restricted:
        cardtable2 = {}
        for key in restricted:
            cardtable2[key] = cardtable[key]
        cardtable = cardtable2
    # TODO This only updates SetData for old cards when we are importing new sets
    if only_sets and len(card)>1 and not latest["card_title"]=="Orb of Wonder":
        pass
    else:
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
            for tt in ct.split(SEPARATOR):
                traits.add(tt)
    return sorted(traits)


if __name__ == "__main__":
    load_from_mv_files()
    print(all_traits())
else:
    load_json()
