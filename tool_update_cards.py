import difflib
import time
import carddb
import wikibase
import card_model_1


def update_page(title, page, text, reason, ot, pause=True):
    if text != ot and pause:
        print("TEXT CHANGE:")
        print(text)
        print("DIFF")
        for l in difflib.context_diff(ot.split("\n"), text.split("\n")):
            print(l)
        print("Changing", title)
        cont = input("Continue?:")
        if cont != "yes":
            raise Exception("You didn't continue")
    if text == ot:
        return None
    if "nochange" in page.edit(text, reason).get("edit", {"nochange": ""}):
        return None
    return text


def put_cargo_on_card_page(wp, card_title, update_reason="Put card query on card page", pause=True):
    page = wp.page(card_title)
    try:
        ot = page.read()
        text = card_model_1.replace_old_card_text(card_title, ot)
    except Exception:
        #TODO build new cardquery
        raise
        return
    return update_page(card_title, page, text, update_reason, ot, pause)


def update_card_page_cargo(wp, card, update_reason="", data_to_update="carddb", pause=True):
    latest = carddb.get_latest_from_card(card)
    page = wp.page("CardData:" + latest["card_title"])
    ct = wikibase.CargoTable()
    ot = ""
    try:
        ot = page.read()
        ct.read_from_text(page.read())
    except Exception:
        pass
    if data_to_update == "carddb":
        carddb.get_cargo(card, ct)
    elif data_to_update == "artist":
        card_model_1.pull_artist(card, ct, wp)
    text = ct.output_text()
    return update_page(page, text, update_reason, ot, pause)


def update_cards_v2(wp, search_name=None,
                    update_reason="phase 2 test",
                    data_to_update="carddb"):
    changed = 0
    started = False
    for i, card_name in enumerate(sorted(carddb.cards.keys())):
        if not started and (search_name and search_name.lower() not in card_name.lower()):
            continue
        started = True
        print(i+1, card_name)
        if data_to_update == "cargo_to_card":
            text = put_cargo_on_card_page(wp, card_name)
        else:
            text = update_card_page_cargo(
                wp, carddb.cards[card_name],
                update_reason=update_reason,
                data_to_update=data_to_update)
        if text:
            print("changed:", text)
            changed += 1
            time.sleep(0.05)
    print(changed, "cards changed")