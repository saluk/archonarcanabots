import difflib
import time
import carddb
import wikibase
from card_model_1 import CardPage

NO_SAVE = 0
SAVE_SANDBOX = 1
SAVE_FULL = 2


def create_card_page(wp, card, load_existing=True, update_mode=NO_SAVE,
                     update_reason="Script testing",
                     pull_from_sandbox=False):

    if not pull_from_sandbox:
        page = wp.page(card["card_title"])
    else:
        page = wp.page("User:Saluk/Sandbox")
    existing = ""
    if(load_existing):
        try:
            existing = page.read()
        except Exception:
            raise
            existing = ""
            print("missing:", card["card_title"])

    card_page = CardPage().from_text(existing)
    card_page.edit_card_field("card_title", card["card_title"])
    card_page.edit_card_field("card_text", card["card_text"])
    card_page.edit_card_field("traits", card["traits"])
    for exp in card["sets"]:
        card_page.edit_card_field("sets", exp[0], exp[1])
    card_page.edit_card_field("armor", card["armor"])
    card_page.edit_card_field("power", card["power"])
    card_page.edit_card_field("amber", card["amber"])
    card_page.edit_card_field("house", card["house"])
    card_page.edit_card_field("type", card["card_type"])
    card_page.edit_card_field("rarity", card["rarity"])
    card_page.edit_card_field("image", card["front_image"])
    print(card_page.sections[0].data)
    print("outputing")
    card_text = card_page.output()

    if card_text == existing:
        return

    # print(repr(existing),repr(card_text))
    print("\n".join(difflib.unified_diff([existing], [card_text])))
    print("edited", card["card_title"])
    if(update_mode == SAVE_FULL):
        page.edit(card_text, update_reason)
    elif(update_mode == SAVE_SANDBOX):
        sandbox = wp.page("User:Saluk/Sandbox")
        sandbox.edit(card_text, update_reason)
    else:
        pass
    time.sleep(0.05)
    return True


def to_cargo_table(d):
    text = "{{%s\n" % d["cargoname"]
    for key in d:
        if key == "cargoname":
            continue
        text += "|%s=%s\n" % (key, d[key])
    text += "}}"
    return text


def create_card_page_cargo(wp, card, update_reason=""):
    latest = carddb.get_latest_from_card(card)
    page = wp.page("CardData:" + latest["card_title"])
    print(card)
    print(page)
    cardtable = {
        "cargoname": "CardData",
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
    text = to_cargo_table(cardtable)
    for (set_name, set_num, card_num) in carddb.get_sets(card):
        text += "\n"+to_cargo_table({
            "cargoname": "SetData",
            "SetName": set_name,
            "SetNumber": set_num,
            "CardNumber": card_num
        })
    """ot = page.read().replace("\u202f", " ")
    if text != ot:
        #print(ot)
        #print(text)
        import difflib
        print("DIFF")
        for l in difflib.unified_diff([ot], [text]):
            print(repr(l))
        print("Changing", latest["card_title"])
        cont = input("Continue?:")
        if cont != "yes":
            crash"""
    if "nochange" in page.edit(text, update_reason).get("edit", {"nochange": ""}):
        return None
    return text


def update_card_page_cargo(wp, card, update_reason=""):
    latest = carddb.get_latest_from_card(card)
    page = wp.page("CardData:" + latest["card_title"])
    ct = wikibase.CargoTable()
    ct.read_from_text(page.read())
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
    for (set_name, set_num, card_num) in carddb.get_sets(card):
        settable = {
            "SetName": set_name,
            "SetNumber": set_num,
            "CardNumber": card_num
        }
        ct.update_or_create("SetData", set_name, settable)
    text = ct.output_text()
    ot = page.read().replace("\u202f", " ")
    if text != ot:
        print("TEXT CHANGE:")
        #print(ot)
        print(text)
        import difflib
        print("DIFF")
        for l in difflib.unified_diff([ot], [text]):
            print(repr(l))
        print("Changing", latest["card_title"])
        cont = input("Continue?:")
        if cont != "yes":
            crash
    print(text)
    if "nochange" in page.edit(text, update_reason).get("edit", {"nochange": ""}):
        return None
    return text


def update_cards(wp, search_name=None, update_mode=NO_SAVE,
                 update_reason="Script testing",
                 pull_from_sandbox=False):
    changed = 0
    for i, card_name in enumerate(carddb.cards):
        card = carddb.collect_latest_card(card_name)
        if search_name and search_name.lower() not in card_name.lower():
            continue
        print(i+1, card_name)
        if create_card_page(wp, card, load_existing=True,
                            update_mode=update_mode,
                            update_reason=update_reason,
                            pull_from_sandbox=pull_from_sandbox):
            changed += 1
    print(changed, "cards changed")


def update_cards_v2(wp, search_name=None,
                    update_reason="phase 2 test"):
    changed = 0
    started = False
    for i, card_name in enumerate(sorted(carddb.cards.keys())):
        if not started and (search_name and search_name.lower() not in card_name.lower()):
            continue
        started = True
        print(i+1, card_name)
        text = update_card_page_cargo(
                wp, carddb.cards[card_name],
                update_reason=update_reason)
        if text:
            print("changed:", text)
            changed += 1
            time.sleep(0.05)
    print(changed, "cards changed")
