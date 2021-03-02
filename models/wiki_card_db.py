import os
import json
import re
from collections import defaultdict
from fuzzywuzzy import fuzz
import sys
sys.path.append("./")
import connections
import util
from util import SEPARATOR
from models import mv_model, wiki_model
import csv
import bleach

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
    name = bleach.clean(name.replace("[", "(").replace("]", ")"))
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
# Enhance is handled custom
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
keywords = [x for x in keywords if x.strip()]

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


def modify_search_text(text):
    # Clean up carriage returns
    text = re.sub("(\r\n|\r|\x0b|\n)", "\r", text)
    # Clean up spaces
    text = re.sub("\u202f", " ", text)
    # Make returns paragraphs
    text = re.sub(r"(\u000b|\r)", " <p> ", text)
    # Replace trailing <p> and spaces
    text = re.sub(r"(<p>| )+$", "", text)
    return text


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

    # Make returns paragraphs
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


def get_latest_from_card(card, locale=None):
    for (set_name, set_num, card_num) in reversed(list(get_sets(card))):
        latest = card[str(set_num)]
        if locale:
            if 'locales' not in latest or locale not in latest['locales']:
                raise Exception("Couldn't find translation for %s" % card)
            latest = latest["locales"][locale]
        return latest
    raise Exception("couldn't find a set in", card)


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


def add_card(card, cards):
    card_data = wiki_model.card_data(card)
    if card_data["card_title"] not in cards:
        cards[card_data["card_title"]] = {}
    cards[card_data["card_title"]][str(card_data["expansion"])] = card_data


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
                add_card(card, cards)

    scope = mv_model.UpdateScope()
    for set_id in [479]:
        for card in scope.get_cards(set_id):
            add_card(card.data, cards)
    for card in scope.get_locale_cards():
        translated_card_data = wiki_model.card_data(card.data, card.locale)
        fixed_data = {"card_title": wiki_model.sanitize_name(card.en_name), "house":card.data["house"], "expansion": card.data["expansion"]}
        wiki_model.fix_card_data(fixed_data)
        entry = cards[fixed_data["card_title"]]
        eng = entry[str(fixed_data['expansion'])]
        if 'locales' not in eng:
            eng['locales'] = {}
        #Don't use english name here
        del fixed_data["card_title"]
        translated_card_data.update(fixed_data)
        translated_card_data["image_number"] = card.locale + "-" + translated_card_data["image_number"]
        eng['locales'][card.locale] = translated_card_data
        continue
        
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
    with open("scribunto/locale_table.lua", "w") as f:
        f.write("--Module:LocaleTable\nlocale_table={}\nlocale_table['traits']={}\n")
        for locale in ['pt-pt', 'it-it', 'zh-hant', 'de-de', 'zh-hans', 'th-th', 'ko-ko', 'pl-pl', 'fr-fr', 'es-es']:
            f.write("locale_table['traits']['%s'] = {}\n" % locale)
            translations = translate_traits(locale)
            for en in translations:
                f.write("locale_table['traits']['%s']['%s'] = '%s'\n" % (locale, en, translations[en]))
        f.write("return locale_table\n")
    print("saved.")


def load_json():
    cards.clear()
    with open("my_card_db.json") as f:
        cards.update(json.loads(f.read()))


def get_latest(card_title, fuzzy=False, locale=None):
    if fuzzy:
        card_title = fuzzyfind(card_title)
    card = get_latest_from_card(cards[card_title], locale)
    return card


def get_restricted_dict(source, restricted, pre=""):
    """ Limits a source dictionary to only the keys in restricted """
    if not restricted:
        return source
    print("restricted",restricted, "pre", pre)
    rd= {}
    for key in source:
        if pre+"."+key in restricted:
            rd[key] = source[key]
    return rd

CARD_FIELDS_FOR_LOCALE = ["EnglishName", "Name", "Image", "Text", "SearchText", "FlavorText", "SearchFlavorText"]
def get_cargo(card, ct=None, restricted=[], only_sets=False, locale=None):
    table = "CardData"
    if not ct:
        from wikibase import CargoTable
        ct = CargoTable()
    latest = get_latest_from_card(card, locale)
    cardtable = get_restricted_dict({
        "Name": latest["card_title"],
        "Image": latest["image_number"],
        "Artist": latest.get("artist", ""),
        "Text": latest["card_text"],
        "SearchText": modify_search_text(latest["card_text_search"]),
        "Keywords": SEPARATOR.join(latest["keywords"]),
        "FlavorText": latest["flavor_text"],
        "SearchFlavorText": modify_search_text(latest["flavor_text_search"]),
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
    }, restricted)
    assert "Artist" not in restricted
    # TODO This only updates SetData for old cards when we are importing new sets
    if only_sets and len(card)>1 and not latest["card_title"]=="Orb of Wonder":
        pass
    else:
        ct.update_or_create(table, 0, cardtable)
    card_sets = list(get_sets(card))
    print(card_sets)
    earliest_set = min([s[1] for s in card_sets])
    print(earliest_set)
    for (set_name, set_num, card_num) in card_sets:
        settable = get_restricted_dict({
            "SetName": set_name,
            "SetNumber": set_num,
            "CardNumber": card_num,
            "Meta":"Debut" if set_num == earliest_set else ""
        }, restricted, "SetData")
        ct.update_or_create("SetData", set_name, settable)
        print(settable)


def get_cargo_locale(card, ct=None, only_sets=False, locale=None, english_name=None):
    fieldset_key = (english_name, locale)
    table = "CardData" if not locale else "CardLocaleData"
    if not ct:
        from wikibase import CargoTable
        ct = CargoTable()
    latest = get_latest_from_card(card, locale)
    cardtable = {
        "Name": latest["card_title"],
        "Image": latest["image_number"],
        "Text": latest["card_text"],
        "SearchText": modify_search_text(latest["card_text_search"]),
        "FlavorText": latest["flavor_text"],
        "SearchFlavorText": modify_search_text(latest["flavor_text_search"]),
        "EnglishName": english_name,
        "Locale": locale
    }
    ct.update_or_create(table, fieldset_key, cardtable)


def all_traits():
    traits = set()
    for card in cards:
        ct = get_latest(card)["traits"]
        if ct:
            for tt in ct.split(SEPARATOR):
                traits.add(tt)
    return sorted(traits)

translation_winners = {
    'power': ['puissance'],
    'ally': ['allié']
}
def translate_traits(locale):
    split_re = re.compile(" • | ·|•|,")
    traits = {}
    errors = []
    for card_key in cards:
        card = cards[card_key]
        en_card = get_latest_from_card(card)
        lang_card = get_latest_from_card(card, locale)
        if en_card['traits'] or lang_card['traits']:
            en_traits, l_traits = [[y.lower().strip() for y in split_re.split(x)] for x in [en_card['traits'], lang_card['traits']]]
            if not len(en_traits) == len(l_traits):
                errors.append((locale, card_key, en_traits, l_traits))
                continue
            for i in range(len(en_traits)):
                en_trait = en_traits[i]
                l_trait = l_traits[i]
                if en_trait not in traits:
                    traits[en_trait] = defaultdict(lambda:list())
                traits[en_trait][l_trait].append(card_key)
    trait_wins = {}
    for t in traits:
        v = traits[t]
        if len(v.keys()) == 1:
            trait_wins[t] = list(v.keys())[0]
        else:
            for w in translation_winners.get(t, []):
                if w in v:
                    trait_wins[t] = w
            w = sorted(v.keys(), key=lambda k: -len(v[k]))[0]
            trait_wins[t] = w
    print("\n\nErrors - ", errors)
    return trait_wins


if __name__ == "__main__":
    load_from_mv_files()
    print(all_traits())
else:
    load_json()
