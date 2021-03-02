import os
import json
import re
from fuzzywuzzy import fuzz
import connections
import util
from util import SEPARATOR
import csv
import bleach


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
    name = name.strip()
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

enhanced_regex = {
    None: "Enhance",
    'fr-fr': "Don",
    'it-it': "Potenziamento",
    'de-de': 'Verbesserung',
    'es-es': 'Potenciar',
    'pl-pl': 'Wzmocnienie',
    'th-th': 'เสริมทัพ',
    'pt-pt': 'Propagar',
    'zh-hans': '强化',
    'zh-hant': '強化',
    'ko-ko': '강화',
    'ru-ru': 'Улучшение'
}
def read_enhanced(text, locale=None):
    # Enhancements
    t = enhanced_regex[locale]
    if locale == 'ko-ko':  # Korean changes the order so we have to special case it
        regex = "((A*)((PT)*)(D*)(R*) %s)"
    else:
        regex = "(%s (A*)((PT)*)(D*)(R*))"
    regex = regex % (t,)
    enhanced = re.match(regex, text)
    ea=ept=ed=er=0
    if enhanced:
        ea = enhanced.group(0).count('A')
        a = "{{Aember}}" * ea
        ept = enhanced.group(0).count('PT')
        pt = "{{Capture}}" * ept
        ed = enhanced.group(0).count('D')
        d = "{{Damage}}" * ed
        er = enhanced.group(0).count('R')
        r = "{{Draw}}" * er
        text = text[:enhanced.start()] + "[[Enhance|%s]] " % t + "".join([a, pt, d, r]) + text[enhanced.end():]
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

    # Make returns paragraphs
    text = re.sub(r"(\u000b|\r)", " <p> ", text)

    # Replace trailing <p> and spaces
    text = re.sub(r"(<p>| )+$", "", text)
    return text


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

def fix_card_data(card, locale=None):
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

def card_data(card, locale=None):
    fix_card_data(card, locale)
    title = sanitize_name(card["card_title"])
    title = safe_name(title)
    card["card_title"] = title
    card["keywords"] = get_keywords_text(card["card_text"])
    card.update({"assault": "", "hazardous": "",
                 "enhance_amber": "", "enhance_damage": "",
                 "enhance_capture": "", "enhance_draw": ""})
    if card["card_type"] in ["Creature1", "Creature2"]:
        if card["card_type"] == "Creature1":
            card["subtype"] = "GiganticTop"
        else:
            card["subtype"] = "GiganticBottom"
        card["card_type"] = "Creature"
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

    card["card_text"], enhancements = read_enhanced(card["card_text"], locale)
    card.update(enhancements)

    card["card_text"] = linking_keywords(modify_card_text(card["card_text"], title))
    card["flavor_text"] = modify_card_text(sanitize_text(card["flavor_text"]), title, flavor_text=True)

    card["image_number"] = image_number(card)
    card["rarity"] = nice_rarity(card["rarity"])

    # Hack because the russian mastervault doesn't provide russian images, but the russian images exist in the cdn
    if locale == 'ru-ru':
        if int(card["expansion"])>=479:
            card["front_image"] = card["front_image"].replace('en', 'ru')

    if card.get("is_anomaly", False):
        card["house"] = "Anomaly"
    if card["traits"]:
        card["traits"] = SEPARATOR.join([sanitize_trait(t) for t in card["traits"].split(SEPARATOR)])

    return card
