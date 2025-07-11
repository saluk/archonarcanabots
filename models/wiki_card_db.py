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
# Just importing mv_model triggers db connect
from models import shared, wiki_model, skyjedi_model #,mv_model
import csv
import bleach
from progress.bar import Bar
import pprint

cards = {}
locales = {}


def sanitize_name(name):
    name = bleach.clean(name.replace("[", "(").replace("]", ")"))
    name = util.dequote(name)
    return name

def sanitize_trait(trait):
    return trait.replace("[","").replace("]","")

card_title_reg_2 = {}
trait_reg = []


blacklist_card_names = [
    "fear"
]

# TODO add token creatures to blacklist:
# select distinct(name) from cards where data->>'card_type'='Token Creature';


linking_titles = []
def link_card_titles(text, original_title):
    # Clean up original title from tags we added that wouldn't be in the card text
    original_title = original_title.replace("(Anomaly)","").replace("(Evil Twin)","").strip()
    if not linking_titles:
        card_title_reg_2.clear()
        linking_titles[:] = sorted([x for x in card_titles_that_link() if not x.lower() in blacklist_card_names])
        for t in linking_titles:
            t = re.sub("\(.*?\)","", t).strip()
            if not t:
                continue
            r = r"(^|[^[a-z])("+re.sub('["””“]', ".", t)+r")([^\]a-z]|$)"
            r = re.compile(r, flags=re.IGNORECASE)
            card_title_reg_2[t] = r
    # Replace self-referential card title with no link
    # Do we allow linking when the title follows a hyphen? This is sometimes used for quotes
    text = re.sub(r"(^|[^[a-z])("+original_title+r")([^\]a-z]|$)", r"\1STITLE\2ETITLE\3", text, flags=re.IGNORECASE)
    links_found = 0
    for (t, r) in card_title_reg_2.items():
        # Replace card titles with link
        text,c = re.subn(r, r"\1[[STITLE"+t+r"|\2ETITLE]]\3", text, count=1)
        # Replace remaining matches with STITLE/ETITLE tags
        text = re.sub(r, r"\1STITLE\2ETITLE\3", text)
        links_found += c
    if links_found:
        print(f"  links found in [{original_title}]: {links_found} -- {text}")
    return text

traits_blacklist = [
    "power"
]
def link_card_traits(card, preload_traits=[]):
    """Must be run after link_card_titles"""
    #First remove any existing trait links
    card["card_text"] = re.sub(r"\[http\:\/\/archonarcana.com\/Card_Gallery\?traits\=.+? (.+?)\]", r"\1", card["card_text"])
    if not trait_reg or preload_traits:
        trait_reg.clear()
        if not preload_traits:
            preload_traits = all_traits()
        card_traits = [t.lower() for t in preload_traits]
        # ignore traits in the blacklist as well as traits that are in card titles
        card_traits = [t for t in card_traits if t not in traits_blacklist]
        card_traits = "|".join(card_traits).replace("(", r"\(").replace(")", r"\)")
        card_traits = re.sub('["””“]', ".", card_traits)
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
            bits[i] = re.sub(trait_reg[0], r'\1[http://archonarcana.com/Card_Gallery?traits=\2 \2]\3', bits[i])
    card["card_text"] = "".join(bits)
    return card["card_text"]

t1 = "After a Mutant creature enters STITLE A Dark Mutant Or Something ETITLE play, enrage Berinon. Reap: Capture 2A."
t2 = "After a [http://archonarcana.com/Card_Gallery?traits=Mutant Mutant] creature enters STITLE A Dark Mutant Or Something ETITLE play, enrage Berinon. Reap: Capture 2A."
card = {"card_text": t1}
t3 = link_card_traits(card, preload_traits=["Mutant"]) 
assert t3 == t2, t3
card = {"card_text": t2}
t4 = link_card_traits(card, preload_traits=["Mutant"])
assert t3==t4, t4
t1 = "'''Action:''' A friendly creature captures 1{{Aember}}. If that creature is a [http://archonarcana.com/Card_Gallery?traits=Dinosaur Dinosaur], it captures 2{{Aember}} [[Replacement Effects|instead]]."
t2 = link_card_traits({"card_text": t1}, preload_traits=["Dinosaur"])
assert t1==t2, t2

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


def get_sets(card_sets):
    sets = sorted(int(x) for x in card_sets.keys())
    for set_num in sets:
        card_for_set = card_sets[str(set_num)]
        card_num = card_for_set["card_number"]
        yield (shared.set_data.assigned_set_name(set_num, card_num), set_num, card_num)


def get_latest_from_card(card_sets, locale=None):
    for (set_name, set_num, card_num) in reversed(list(get_sets(card_sets))):
        latest = card_sets[str(set_num)]
        if locale:
            if locale not in locales or latest["card_title"] not in locales[locale]:
                raise Exception("Couldn't find translation for %s" % card_sets)
            latest = locales[locale][latest["card_title"]]
        return latest
    raise Exception("couldn't find a set in", card_sets)


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


def card_titles_that_link():
    return [x for x in get_card_titles() if not x.lower() in blacklist_card_names]


def get_card_by_number(num, expansion):
    num_index = {}
    for card in cards:
        for setid in cards[card]:
            card_in_set = cards[card][setid]
            num_index[(card_in_set["card_number"], setid)] = cards[card]
    if type(num)==type(1):
        num = ("000"+str(num))[-3:]
    return num_index[(num, str(expansion))]


def add_card(card, cards, bar=None):
    #print(f"+ Get card data for {card}")
    card_data = wiki_model.card_data(card)
    if "'" in card_data["card_title"]:
        print(card_data)
        crash
    if card_data["card_title"] not in cards:
        cards[card_data["card_title"]] = {}
    cards[card_data["card_title"]][str(card_data["expansion"])] = card_data
    #add_artists_from_text(cards)
    #build_links([card_data["card_title"]])
    clean_fields_data(card_data)
    if bar:
        bar.next()
    return card_data


def build_localization(scope, cards, locales, from_cards=None):
    print("+build localization")
    if from_cards is None:
        from_cards = list(scope.get_locale_cards())
    for card in from_cards:
        #print("card data-ify",card.en_name)
        translated_card_data = wiki_model.card_data(card.data, card.locale)
        english_data = {}
        english_data.update(translated_card_data)
        #print("sanitize and rename english name")
        english_data["card_title"] = wiki_model.sanitize_name(card.en_name)
        wiki_model.rename_card_data(english_data)
        entry = cards[english_data["card_title"]]
        # If there's a higher set version of this card, don't translate it
        if english_data["expansion"] != list(get_sets(entry))[-1][1]:
            continue
        eng = entry[str(english_data['expansion'])]
        # #Don't use english name here
        # del english_data["card_title"]
        # translated_card_data.update(english_data)
        use_english = False
        if card.locale == "ru-ru" and not int(card.data['expansion']) >= 479:
            use_english = True
        if card.locale == "ko-ko" and not int(card.data['expansion']) > 341:
            use_english = True
        if not use_english:
            translated_card_data["image_number"] = card.locale + "-" + translated_card_data["image_number"]
        if card.locale not in locales:
            locales[card.locale] = {}
        locales[card.locale][english_data["card_title"]] = translated_card_data


def build_links(card_dict, only=None, bar=None):
    print("+build links")
    for card_title in card_dict:
        if only and card_title != only:
            continue
        card = get_latest(card_title, card_dict)
        if card.get("_linking_finished", False):
            continue
        card["flavor_text"] = link_card_titles(card["flavor_text"], card_title) #leaves behind stitle/etitle tags
        card["card_text"] = link_card_titles(card["card_text"], card_title)  #leaves behind stitle/etitle tags
        link_card_traits(card)  #uses stitle/etitle tags to avoid covering the same ground
        #Clean up stitle/etitle tags
        card["card_text"] = re.sub("(STITLE|ETITLE)", "", card["card_text"])
        card["flavor_text"] = re.sub("(STITLE|ETITLE)", "", card["flavor_text"])
        card["_linking_finished"] = True
        if bar:
            bar.next()


def add_artists_from_text(cards):
    print("+add artists")
    for setn in shared.get_set_numbers():
        fn = f"data/artists_{setn}.csv"
        if not os.path.exists(fn):
            continue
        with open(fn) as f:
            header = False
            for line in csv.reader(f):
                if not header:
                    header = True
                    continue
                num, artist = line
                try:
                    card = get_card_by_number(int(num), setn)
                except:
                    continue
                card[str(setn)]["artist"] = artist


def save_json(cards, locales, build_locales=False):
    with open("data/my_card_db.json", "w") as f:
        f.write(json.dumps(cards, indent=2, sort_keys=True))
    if build_locales:
        with open("data/my_card_db_locales.json", "w") as f:
            f.write(json.dumps(locales, indent=2, sort_keys=True))

ignore_fields = ["deck_expansion"]
def clean_fields_data(data):
    for key in list(data.keys()):
        if key.startswith("_") or key in ignore_fields:
            del data[key]

def clean_fields(cards, locales):
    print("+clean fields")
    for card_name, set_data in cards.items():
        for set_name, card_data in set_data.items():
            clean_fields_data(card_data)
    for locale, locale_data in locales.items():
        for english_name, card_data in locale_data.items():
            clean_fields_data(card_data)


def process_mv_card_batch(card_batch: list) -> list:
    """Prepare a batch of cards queried from the mastervault."""

    same_title_cards = defaultdict(lambda: [])
    for card in card_batch:
        #if not card.is_from_current_set:
        #    continue
        #if card.is_maverick: continue
        #if card.is_enhanced: continue
        same_title_cards[card.data["card_title"]].append(card.data)

    return process_card_batch(same_title_cards)


def process_skyjedi_card_batch(card_batch: list) -> list:
    """Prepare a batch of raw MV JSON cards. This prefers SkeyJedi
       but will also look for MVlite scraped card sets."""

    same_title_cards = defaultdict(lambda: [])
    for card in card_batch:
        same_title_cards[card["card_title"]].append(card)

    return process_card_batch(same_title_cards)


def process_card_batch(same_title_cards: dict) -> list:
    import logging
    logging.debug(len(same_title_cards))
    print(f"\n+++ Process these cards: {len(same_title_cards)} - {same_title_cards.keys()}\n")

    card_datas = []
    for _card_datas in same_title_cards.values():
        card_datas.extend(bifurcate_data(_card_datas))
    logging.debug([card["card_title"] for card in card_datas])

    return card_datas


def bifurcate_data(card_datas):
    """For a set of cards, isolate them into the list of cards
    we want to put onto Archon Arcana as individual card pages. Some cards with the same name in the db
    will be merged into one card (such as a card that can appear in multiple houses), while others will be
    separated into multiple cards (Anomaly version of a card and the non-Anomaly version of the card)
    Returns a list of card data dictionaries that something else can process

    Input: card_datas is a list of card dictionaries
    Each dict is one MV card JSON all with the same card title.

    Output: a list of card dict where we've done any of:
      - merged dicts, like two halves of gigantic into one dict
      - split the list into distinct dicts, like an anomly or
        redemption variant distinct from the normal card"""
    # TODO clean up when we refactor card db stuff to a class
    # TODO - note, to combine houses, this method requires the batch to include the complete set of cards of a given name

    if not card_datas:
        return []

    # Prophecies and Archon Powers just get some
    # schema manipulation.
    (has38s, the38s, other) = bifurcate_38s(card_datas)
    if has38s:
        return the38s + bifurcate_data(other)

    # Cards that are new and only in Redemption are
    # fine to leave alone. When a card has been in
    # another house and then house-shifted into Redemption,
    # it needs a variant title.
    (
        has_mixed_redemption, redemption, other
    ) = bifurcate_redemption(card_datas)
    if has_mixed_redemption:
        return redemption + bifurcate_data(other)

    # Special house variants should happen even when
    # it is the only card_data, like Agent Taengoo
    # debut in MCW.
    (
        has_martian_faction, faction, other
    ) = bifurcate_martian_faction(card_datas)
    if has_martian_faction:
        return faction + bifurcate_data(other)

    if len(card_datas) == 1:
        return card_datas

    (
        is_giant, merged_halves
    ) = bifurcate_giants(card_datas)
    if is_giant:
        return merged_halves

    (
        has_anomaly, anomalies, other
    ) = bifurcate_anomalies(card_datas)
    if has_anomaly:
        return anomalies + bifurcate_data(other)

    # Do special multi-house cases before this, like Redemption.
    # We may never get to this case if we're not doing high
    # MV API QPS and building card data from scanned decks of
    # a yet unknown set list.
    (
        multi_house, merged
    ) = bifurcate_multi_house(card_datas)
    if multi_house:
        return merged

    # We shouldn't fall to this case and still have
    # multiple types.
    types = set([card["card_type"] for card in card_datas])
    if len(types) > 1:
        card_title = card_datas[0]["card_title"]
        print(card_datas)
        raise Exception(f"Unknown type mismatch {card_title} {types}")

    # Otherwise the batch doesn't need bifurcation.
    return card_datas


def bifurcate_38s(card_datas):
    """Returns (has38s, the38s, other)"""

    variable38s = ["Prophecy", "Archon Power"]

    has38s = False
    the38s = []
    other = []
    for data in card_datas:
        if data["house"] in variable38s:
            has38s = True
            new_data = {}
            new_data.update(data)
            new_data["house"] = None
            new_data["card_type"] = "38th Card"
            the38s.append(new_data)
        else:
            other.append(data)

    return (has38s, the38s, other)


def bifurcate_giants(card_datas):
    """Returns (is_giant, merged_halves)"""

    card_title = card_datas[0]["card_title"]

    texts = set([card["card_text"] for card in card_datas])

    is_giant = False
    for t in texts:
        if "Play only with the other half of" in t:
            is_giant = True
            break

    if not is_giant:
        return (is_giant, [])

    # Okay, giants. Separate by expansion and we expect
    # have exactly two cards each. Then different expansions
    # have different schema for finding the merged AA data.

    same_exp = defaultdict(lambda: [])
    for data in card_datas:
        same_exp[data["expansion"]].append(data)

    merged_halves = []
    for _, batch in same_exp.items():
        if len(batch) != 2:
            pprint.pp(card_datas)
            raise Exception(
                "Giants weren't two halves per expansion?"
            )

        if batch[0]["card_type"] in ["Creature1", "Creature2"]:
            # MM style
            cre1 = None
            cre2 = None
            if batch[0]["card_type"] == "Creature1":
                cre1 = batch[0]
                cre2 = batch[1]
            else:
                cre1 = batch[1]
                cre2 = batch[0]

            new_data = {}
            new_data.update(cre1)
            new_data["card_type"] = "Creature"
            merged_halves.append(new_data)

        else:
            # MoMu style
            assert(batch[0]["card_type"] == "Creature")
            assert(batch[1]["card_type"] == "Creature")

            keep = None
            drop = None
            if batch[0]["card_text"]:
                keep = batch[0]
                drop = batch[1]
            else:
                keep = batch[1]
                drop = batch[0]

            # We want keep's data except drop's rarity.
            new_data = {}
            new_data.update(keep)
            new_data["rarity"] = drop["rarity"]
            merged_halves.append(new_data)

    return (is_giant, merged_halves)


def bifurcate_anomalies(card_datas):
    """Returns (has_anomaly, anomalies, other)"""

    has_anomaly = False
    anomalies = []
    other = []
    for data in card_datas:
        if data.get("is_anomaly", False):
            has_anomaly = True
            anomalies.append(data)
        else:
            other.append(data)

    return (has_anomaly, anomalies, other)


def bifurcate_redemption(card_datas):
    """Returns (has_mixed_redemption, redemption, other)"""

    houses = set([card["house"] for card in card_datas])
    has_redemption = "Redemption" in houses
    has_mixed_redemption = has_redemption and len(houses) > 1
    redemp = []
    other = []

    for data in card_datas:
        if data.get("house", None) == "Redemption" \
           and has_mixed_redemption:
            # The same card moving houses to Redemption
            # in a different set becomes a different
            # wiki page.
            new_data = {}
            new_data.update(data)
            new_data["card_title"] += " (Redemption)"
            redemp.append(new_data)
        else:
            other.append(data)

    return (has_mixed_redemption, redemp, other)


def bifurcate_martian_faction(card_datas):
    """Returns (has_martian_faction, faction, other)"""

    houses = set([card["house"] for card in card_datas])
    has_faction = "Elders" in houses or \
        "Ironyx Rebels" in houses
    faction = []
    other = []

    for data in card_datas:
        if data.get("house", None) == "Elders" or \
           data.get("house", None) == "Ironyx Rebels":
            # The same card being in a Martian faction
            # in a different set becomes a different
            # wiki page.
            new_data = {}
            new_data.update(data)
            new_data["card_title"] += \
                " (" + data.get("house", None) + ")"
            faction.append(new_data)
        else:
            other.append(data)

    return (has_faction, faction, other)


def bifurcate_multi_house(card_datas):
    """Returns (multi_house, merged)"""

    houses = set([card["house"] for card in card_datas])
    multi_house = len(houses) > 1
    merged = []

    if multi_house:
        new_data = {}
        new_data.update(card_datas[0])
        new_data["house"] = util.SEPARATOR.join(sorted(houses))
        merged = [new_data]

    return (multi_house, merged)


def build_json(only=None, build_locales=False, from_skyjedi=False, from_mvlite=False):
    print("++++ Clear memory")
    cards.clear()

    if build_locales:
        locales.clear()

    card_datas = None
    if from_skyjedi:
        print("++++ Getting card batch from skyjedi json")
        local_json = skyjedi_model.LocalJson()

        # Historically haven't added menagerie.
        skipsets = [601, 722]

        # Prefer skyjedi file, then if enabled mvlite files.
        print("JSON files to include:")
        for set_code in shared.SETS.keys():
            if set_code in skipsets:
                continue

            if os.path.exists(f"skyjedi/{set_code}.json"):
                print(f"  skyjedi/{set_code}.json")
                local_json.add_file(f"skyjedi/{set_code}.json")

            elif from_mvlite:
                if os.path.exists(f"data/mvlite_cards_{set_code}.json"):
                    print(f"  data/mvlite_cards_{set_code}.json")
                    local_json.add_file(f"data/mvlite_cards_{set_code}.json")

        card_batch = local_json.get_cards()
        print("++++ Processing batch")
        card_datas = process_skyjedi_card_batch(card_batch)
    else:
        print("++++ Getting card batch from postgresql")
        scope = mv_model.UpdateScope()
        card_batch = scope.get_cards()
        print("++++ Processing batch")
        card_datas = process_mv_card_batch(card_batch)

    # add_card() leads to more card/text processing in wiki_model.
    print("++++ Adding cards")
    with Bar("Adding Cards", max=len(card_datas)) as bar:
        [add_card(card_data, cards, bar) for card_data in card_datas]
    print(f"++++ Cards initialized: {len(cards.keys())}")

    if build_locales:
        print("++++  Building localization")
        build_localization(scope, cards, locales)

    print("++++  Building links")
    with Bar("Cards linked:", max=len(cards)) as bar:
        build_links(cards, only, bar)

    print("++++  Adding artists")
    add_artists_from_text(cards)

    print("++++  Cleaning fields on cards in locales")
    clean_fields(cards, locales)

    print("++++  Saving json")
    save_json(cards, locales, build_locales)
    print("++++  saved.")


# TODO - we should separate creating and loading the data so that the google actions test doesnt have to import the database
def load_json():
    cards.clear()
    locales.clear()
    if os.path.exists("data/my_card_db.json"):
        with open("data/my_card_db.json") as f:
            cards.update(json.loads(f.read()))
    if os.path.exists("data/my_card_db_locales.json"):
        with open("data/my_card_db_locales.json") as f:
            locales.update(json.loads(f.read()))


def get_latest(card_title, card_dict=cards, fuzzy=False, locale=None):
    if fuzzy:
        card_title = fuzzyfind(card_title)
    card = get_latest_from_card(card_dict[card_title], locale)
    card["is_latest"] = True
    return card


def get_restricted_dict(source, restricted, pre=""):
    """ Limits a source dictionary to only the keys in restricted """
    if not restricted:
        return source
    rd= {}
    if pre:
        pre = pre+"."
    for key in source:
        if pre+key in restricted:
            rd[key] = source[key]
    return rd

CARD_FIELDS_FOR_LOCALE = ["EnglishName", "Name", "Image", "Text", "SearchText", "FlavorText", "SearchFlavorText"]
def get_cargo(card, ct=None, restricted=[], only_sets=False, locale=None, prevent_spoilers=False):
    table = "CardData"
    if not ct:
        from wikibase import CargoTable
        ct = CargoTable()
    latest = get_latest_from_card(card, locale)
    cardtable = get_restricted_dict({
        "Name": latest["card_title"],
        "Image": latest["image_number"],
        "Text": latest["card_text"],
        "SearchText": latest["card_text_search"],
        "Keywords": SEPARATOR.join(latest["keywords"]),
        "FlavorText": latest["flavor_text"],
        "SearchFlavorText": latest["flavor_text_search"],
        "Power": latest["power"],
        "Armor": latest["armor"],
        "Amber": latest["amber"],
        "Assault": latest["assault"],
        "Hazardous": latest["hazardous"],
        "EnhanceDamage": latest["enhance_damage"],
        "EnhanceAmber": latest["enhance_amber"],
        "EnhanceDraw": latest["enhance_draw"],
        "EnhanceCapture": latest["enhance_capture"],
        "EnhanceDiscard": latest["enhance_discard"],  # TODO Check value of EnhanceDiscard from master vault
        "Type": latest["card_type"],
        "House": latest["house"],
        "Traits": latest["traits"],
        "Rarity": latest["rarity"]
    }, restricted)
    if latest.get("artist", ""):
        cardtable["Artist"] = latest["artist"]
    # TODO This only updates SetData for old cards when we are importing new 
    if not only_sets:
        ct.update_or_create(table, cardtable["Name"], cardtable)
    card_sets = list(get_sets(card))
    earliest_set = min([int(s[1]) for s in card_sets])
    for (set_name, set_num, card_num) in card_sets:
        settable = get_restricted_dict({
            "SetName": set_name,
            #"SetNumber": set_num,
            "CardNumber": card_num,
            "Meta":"Debut" if set_num == earliest_set else ""
        }, restricted, "SetData")
        # FIXME - this is hacky, but if the set is in spoilers, rewrite the meta
        if not prevent_spoilers and shared.set_data.is_spoiler(settable["SetName"]):
            settable["Meta"] = "SpoilerNew" if settable["Meta"] == "Debut" else "SpoilerReprint"
        ct.update_or_create("SetData", set_name, settable)
    return ct


def get_cargo_locale(card, ct=None, only_sets=False, locale=None, english_name=None):
    fieldset_key = (english_name, locale)
    table = "CardData" if not locale else "CardLocaleData"
    if not ct:
        from wikibase import CargoTable
        ct = CargoTable()
    latest = get_latest_from_card(card, locale)
    # IF the localized card image is in english, just use the english image
    if locale and "/en/" in latest["front_image"] and locale in latest["image_number"]:
        latest["image_number"] = "-".join(latest["image_number"].split("-")[-2:])
    cardtable = {
        "Name": latest["card_title"],
        "Image": latest["image_number"],
        "Text": latest["card_text"],
        "SearchText": latest["card_text_search"],
        "FlavorText": latest["flavor_text"],
        "SearchFlavorText": latest["flavor_text_search"],
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


with open("data/locales.json") as f:
    locale_db = json.loads(f.read())

def translate_all_traits():
    with open("scribunto/locale_table.lua", "w") as f:
        f.write("--Module:LocaleTable\nlocale_table={}\nlocale_table['traits']={}\n")
        for locale in locale_db.keys():
            if locale == "en": continue
            f.write("locale_table['traits']['%s'] = {}\n" % locale)
            translations = translate_traits(locale)
            for en in translations:
                f.write("locale_table['traits']['%s']['%s'] = '%s'\n" % (locale, en, translations[en]))
        f.write("return locale_table\n")
    for locale in locale_db.keys():
        if locale == "en": continue
        with open("data/traits/"+locale+".json", "w") as f:
            translations = translate_traits(locale)
            f.write(json.dumps(translations, indent=4))

def earliest_locale_expansion(locale):
    if locale == 'ko-ko':
        return 479
    if locale == 'ru-ru':
        return 479
    if locale == 'th-th':
        return 435
    return 0

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
        if int(lang_card['expansion']) < earliest_locale_expansion(locale):
            continue
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


load_json()

def testing_linking_pingle_on_blood_of_titans():
    print("\nSTART\n")
    scope = mv_model.UpdateScope()
    card_batch = scope.get_cards()
    batches = []
    for card in card_batch:
        if card.name != "Blood of Titans" and card.name != "Pingle Who Annoys":
            continue
        batches.append(card)
    card_datas = process_mv_card_batch(batches)
    print(card_datas)
    test_cards = {}
    [add_card(card_data, test_cards) for card_data in card_datas]
    print(test_cards)
    build_links(test_cards)
    print(test_cards)

def testing_enhance_on_Grammaticus_Thrax():
    print("\nSTART\n")
    scope = mv_model.UpdateScope()
    card_batch = scope.get_cards()
    batches = []
    for card in card_batch:
        if card.name != "Grammaticus Thrax":
            continue
        batches.append(card)
    card_datas = process_mv_card_batch(batches)
    print(card_datas)
    test_cards = {}
    [add_card(card_data, test_cards) for card_data in card_datas]
    print(test_cards)
    build_links(test_cards)
    print(test_cards)
