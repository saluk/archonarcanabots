import os
import json
import re
from fuzzywuzzy import fuzz
import connections
import util
from util import SEPARATOR
import csv
import bleach
from models import shared
import re
import copy


hard_code = {
    "Exchange Officer": {
        "update": {
            "house": "Star Alliance"
        }
    }
}


unicode_to_icon_letter = {
    '\uf360': 'A',
    '\uf565': 'PT',
    '\uf36f\uf560': 'PT',
    '\uf560': 'PT',
    '\uf361': 'D',
    '\uf36e': 'R'
}

icon_letter_to_wiki_text = {
    'A': '{{Aember}}',
    'PT': '{{Capture}}',
    'D': '{{Damage}}',
    'R': '{{Draw}}',
    '\uf372': '{{Discard}}'
}

unicode_to_wiki_text = {}
for k in unicode_to_icon_letter:
    unicode_to_wiki_text[k] = icon_letter_to_wiki_text[unicode_to_icon_letter[k]]
unicode_or_icon_letter_to_wiki_text = {}
unicode_or_icon_letter_to_wiki_text.update(unicode_to_wiki_text)
unicode_or_icon_letter_to_wiki_text.update(icon_letter_to_wiki_text)


def multiple_replace(string, rep_dict):
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)

# Confirmed these are called by skyjedi JSON build path.
# But they are passed wikitext that uses for example
# simple quotes for formatting. Don't want to mess with
# the bigger design, will deal with raw simple vs fancy
# quotes in skyjedi_model.py

def sanitize_name(name):
    name = bleach.clean(name.replace("[", "(").replace("]", ")"))
    name = util.dequote(name)
    name = name.strip()
    return name

def sanitize_trait(trait):
    return trait.replace("[","").replace("]","")

def sanitize_text(text, flavor=False):
    t = re.sub("(?<!\.)\.\.{1}$", ".", text)
    t = t.replace("_x000D_", '\r')
    t = t.replace("\ufeff", "")
    t = t.replace("\u202f", " ")
    t = t.replace("\xa0", " ")
    t = re.sub("(\u2011|\u2013|\u2014)", "-", t)
    t = t.replace("<softreturn>", "\r")
    t = t.replace("<nonbreak>", " ")
    if flavor:
        t = re.sub(" *(\n|\r\n) *", " ", t)
    # Hack because of dust pixie and virtuous works
    if t.strip() in ["(Vanilla)", "0"]:
        t = ""
    return t.strip()


def test_sanitize():
    assert sanitize_text("blah.") == "blah.", sanitize_text("blah.")
    assert sanitize_text("blah..") == "blah.", repr(sanitize_text("blah.."))
    assert sanitize_text("blah") == "blah"
    assert sanitize_text("blah... something") == "blah... something"
    assert sanitize_text("blah...") == "blah...", sanitize_text("blah...")
    assert sanitize_text("'''Play:''' Deal 4{{Damage}} to a creature that is not on a [[Flank|flank]], with 2{{Damage}} [[Splash|splash]].\ufeff\ufeff") == "'''Play:''' Deal 4{{Damage}} to a creature that is not on a [[Flank|flank]], with 2{{Damage}} [[Splash|splash]]."
    assert sanitize_text("\u201cThe Red Shroud will defend the Crucible\r\nfrom the threat of dark \u00e6mber.\u201d", flavor=True) == "\u201cThe Red Shroud will defend the Crucible from the threat of dark \u00e6mber.\u201d", repr(sanitize_text("\u201cThe Red Shroud will defend the Crucible\r\nfrom the threat of dark \u00e6mber.\u201d", flavor=True))
    assert sanitize_text("something    \n    something else", flavor=True)=="something something else"
    print(repr(sanitize_text("\u201cThe sky\u2019s the limit...for now.\u201d <softreturn>\u2014Dr.<nonbreak>Verokter", flavor=True)))
    assert sanitize_text("\u201cThe sky\u2019s the limit...for now.\u201d <softreturn>\u2014Dr.<nonbreak>Verokter", flavor=True) == "\u201cThe sky\u2019s the limit...for now.\u201d \r-Dr. Verokter"

test_sanitize()

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
Taunt
Splash-attack
Treachery
Versatile""".split("\n")
keywords = [x for x in keywords if x.strip()]

replacement_links = {
    "Splash-attack": "Splash-Attack_(X)",
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
    "forging keys": "Forge",
    "forge a key": "Timing_Chart#Forge_a_Key",
    "current cost": "Cost",
    "cost": "Cost",
    "spent": "Forge",
    "spend": "Forge",
    "take control": "Control",
    "control": "Control",
    "for each": "For each",
    "tide": "Tide",
    "cannot": "Cannot_vs_Must",
    "token creature": "Token Creatures",
    "token creatures": "Token Creatures",
    "haunted": "Haunted"
    # TODO - ready and fight
}
for kw in keywords:
    replacement_links[kw.lower()] = kw.capitalize()

remove_links = [
    "return",
    "archive",
    "archives"
]
remove_links_regex = [
    re.compile(r"\[\[[^]]*?\|{0,1}("+kw+r")\]\]", re.IGNORECASE) for kw in remove_links
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
    t = enhanced_regex.get(locale, enhanced_regex[None])
    enhance_characters = list(unicode_to_icon_letter.keys()) + list(icon_letter_to_wiki_text.keys())
    enhance_character_join = "|".join(enhance_characters)
    if locale == 'ko-ko':  # Korean changes the order so we have to special case it
        regex = f"(\(*(({enhance_character_join})*)\)* {t})"
    else:
        regex = f"(({t}) \(*(({enhance_character_join})*)\)*)"
    enhanced = re.match(regex, text)
    ea=ept=ed=er=ediscard=0
    if enhanced:
        replaced_text = multiple_replace(enhanced.group(3), unicode_or_icon_letter_to_wiki_text)
        print("replaced:", replaced_text)
        ea = replaced_text.count("{{Aember}}")
        ept = replaced_text.count("{{Capture}}")
        ed = replaced_text.count("{{Damage}}")
        er = replaced_text.count("{{Draw}}")
        ediscard = replaced_text.count("{{Discard}}")
        text = text[:enhanced.start()] + "[[Enhance|%s]] " % t + replaced_text + text[enhanced.end():]
    return text, {'enhance_amber':ea, 'enhance_capture':ept, 'enhance_damage':ed, 'enhance_draw':er, 'enhance_discard':ediscard}

print(read_enhanced("Enhance \uf360\uf360\uf360\uf36e\uf361\uf361\uf565\uf565\uf565\uf565"))
print(read_enhanced("\uf360\uf360\uf360\uf36e\uf361\uf361\uf565\uf565\uf565\uf565 강화", "ko-ko"))
print(read_enhanced("Enhance (\uf565\uf565). (These icons have already been added to cards in your deck.) <p> Reap: Exhaust a creature."))
print(read_enhanced("Enhance . (These icons have already been added to cards in your deck.)\n")) # Aember, Aember, Damage

def modify_card_text(text, card_title, flavor_text=False):
    # Clean up carriage returns
    text = re.sub("(\r\n|\r|\x0b|\n)", "\r", text)
    # Clean up spaces
    text = re.sub("(\u202f|\u00a0|\xa0)", " ", text)

    # Turn <A> or something A or 1A or +A or -A into {{Aember}} or {{Aember}} or 1{{Aember}}
    if not flavor_text:
        # If there is an "A" at the begining of a sentance, don't replace it
        # Po's Pixies has an aember symbol at the begining of a sentance
        if card_title not in ["Po’s Pixies", "Sack of Coins"]:
            text = re.sub(r"(^|: |\. |\r)A", r"\1$A$", text)

        # Different from read_enhanced, as these icons can appear elsewhere in card text
        for k in unicode_or_icon_letter_to_wiki_text:
            v = unicode_or_icon_letter_to_wiki_text[k]
            text = re.sub(r"( |\+|\-|–|\r|\+X)(\d+)*\<{0,1}("+k+")\>{0,1}( |$|\.|\,)", r"\1\2"+v+r"\4", text)
        # Tide icon
        text = re.sub(r"\uf566", r"{{Tide}}", text)

        # Replace A's at the begining of the sentance again
        text = re.sub(r"\$A\$", "A", text)
        # bold abilities at the begining of a line or following a new line, or following a tide icon
        # locale = en
        text = re.sub(r"(^|\r|“|‘|\"| *{{Tide}} *)((\w|\/| )+\:)", r"\1'''\2'''", text)
        # locale.startswith('zh') - different colon symbol
        # text = re.sub(r"(^|\r|“|‘)((\w|\/| )+\：)", r"\1'''\2'''", text)
        # locale == 'th' - maybe wrong \w?
        # text = re.sub(r"(^|\r|“|‘)((\w|\/| )+\:)", r"\1'''\2'''", text)
        # locale == 'fr' - extra space between word and quote?
        # text = re.sub(r"(^|\r|“|‘)((\w|\/| )+\:)", r"\1'''\2'''", text)

    # Make returns paragraphs
    text = re.sub(r"(\u000b|\r)", " <p> ", text)

    # Replace trailing <p> and spaces
    text = re.sub(r"(<p>| )+$", "", text)
    return text

print(repr(modify_card_text("[[Enhance|Enhance]] {{Aember}}{{Aember}}{{Damage}}{{Damage}}{{Draw}}{{Draw}}.  <p> When resolving a bonus icon, you may choose to resolve it as a \uf36f\uf560 bonus icon [[Replacement Effects|instead]].", "")))

def modify_search_text(text):
    # Clean up carriage returns
    text = re.sub("(\r\n|\r|\x0b|\n)", "\r", text)
    # Clean up spaces
    text = re.sub("\u202f", " ", text)
    # Make returns paragraphs
    text = re.sub(r"(\u000b|\r)", " <p> ", text)
    # Replace trailing <p> and spaces
    text = re.sub(r"(<p>| )+$", "", text)
    # All unicode maps
    text = multiple_replace(
        text, unicode_to_icon_letter
    )
    return text

print(repr(modify_search_text('After Reap: Give control of a friendly artifact to your opponent. If you do, they must give you 2\uf360.')))

def linking_keywords(text):
    for kwr in remove_links_regex:
        text = kwr.sub(r"\1", text)
    for kw in sorted(replacement_links, key=lambda s: -len(s)):
        debracket = re.split(r"(\[\[.*?\]\]|\{\{.*?\}\})", text)
        rep = not (debracket[0].startswith("[[") or debracket[0].startswith("{{"))
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


print(linking_keywords("{{Tide}} Raise the Tide"))


def nice_rarity(rarity):
    if rarity == "FIXED":
        return "Fixed"
    return rarity


def image_number(card):
    return "%s-%s.png" % (card["expansion"], card["card_number"])

def rename_card_data(card_data, locale=None):
    # We probably DO want to modify in place
    #card_data = copy.deepcopy(card_data)
    ot = sanitize_name(card_data["card_title"])

    if ot in hard_code:
        commands = hard_code[ot]
        card_data.update(commands.get("update", {}))
        for exp in commands.get("rename_expansion", {}):
            if exp != card_data["expansion"]:
                continue
            new_name = commands["rename_expansion"][exp]
            new_name = new_name.replace("%s", ot)
            ot = new_name
        subs = commands.get("substitute", {})
        for subk in subs:
            for field in card_data.keys():
                if hasattr(card_data[field], "replace"):
                    card_data[field] = card_data[field].replace(subk, subs[subk])

    title_modifications = []
    if card_data.get("is_anomaly", False):
        card_data["house"] = "Anomaly"
        title_modifications.append("Anomaly")

    if shared.is_evil_twin(card_data):
        title_modifications.append("Evil Twin")

    if title_modifications:
        ot += " (%s)" % ", ".join(title_modifications)

    card_data["card_title"] = ot
    return card_data


def card_data(card, locale=None):
    # We probably don't want to modify this in place
    card = copy.deepcopy(card)
    rename_card_data(card, locale)
    title = card["card_title"]
    card["keywords"] = get_keywords_text(card["card_text"])
    card.update({"assault": "", "hazardous": "",
                 "enhance_amber": "", "enhance_damage": "",
                 "enhance_capture": "", "enhance_draw": "",
                 "enhance_discard": ""})
    if card["card_type"] in ["Creature1", "Creature2"]:
        if card["card_type"] == "Creature1":
            card["subtype"] = "GiganticTop"
        else:
            card["subtype"] = "GiganticBottom"
        card["card_type"] = "Creature"
    if card["card_type"] == "Creature":
        card["assault"] = get_keywordvalue_text(card["card_text"], "assault") or 0
        card["hazardous"] = get_keywordvalue_text(card["card_text"], "hazardous") or 0

        if card["power"]:
            # Motivating case is "X" power creatures, but AA schema
            # needs an integer value.
            try:
                card["power"] = int(card["power"])
            except ValueError:
                card["power"] = 0
        else:
            card["power"] = 0

        if card["armor"]:
            try:
                card["armor"] = int(card["armor"])
            except ValueError:
                card["armor"] = 0
        else:
            card["armor"] = 0

    else:
        if card["power"] and not int(card["power"]):
            card["power"] = ""
        if card["armor"] and not int(card["armor"]):
            card["armor"] = ""

    card["card_text"] = sanitize_text(card["card_text"] or "")
    card["flavor_text"] = sanitize_text(card["flavor_text"] or "", flavor=True)

    card["card_text_search"] = modify_search_text(card["card_text"])
    card["flavor_text_search"] = modify_search_text(card["flavor_text"])

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

    if card["traits"]:
        card["traits"] = SEPARATOR.join([sanitize_trait(t) for t in card["traits"].split(SEPARATOR)])

    return card
