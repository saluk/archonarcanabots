import difflib
import time
import carddb
import wikibase
import card_model_1
import requests
import os
import shutil
import json

reprints = {"edited":{}, "errata":{}}
with open("data/reprint_update.csv") as f:
    name = old = new = None
    for line in f.read().split("\n"):
        print(repr(line))
        if not name:
            name = line.split("\t")[0]
            continue
        if not old:
            old = line.split("\t")
            continue
        if not new:
            new = line.split("\t")
            etype = "errata"
            if "saluk" in old[1] or "saluk" in new[1]:
                etype = "edited"
            v = {"old":old[0], "new":new[0]}
            print("add", name, v, etype)
            reprints[etype][name] = v
            name=old=new=None

print(reprints["errata"]["Transporter Platform"])

csv_changes = open("changes.csv","w")

skip_status = {}
if os.path.exists("skips.json"):
    with open("skips.json") as f:
        skip_status = json.loads(f.read())
def add_skip(name):
    skip_status[name] = {"skipped":True}
    with open("skips.json", "w") as f:
        f.write(json.dumps(skip_status))


def update_page(title, page, text, reason, ot, pause=False):
    if title in skip_status:
        print("skipping", title)
        return
    if text != ot and pause:
        print("DIFF")
        for l in difflib.context_diff(ot.split("\n"), text.split("\n")):
            print(l)
        print("Changing", title)
        cont = input("(k)eep, (upd)ate, or anything else to ask later:")
        if cont == "k":
            add_skip(title)
        if cont != "upd":
            return
    if text == ot:
        return None
    if "nochange" in page.edit(text, reason).get("edit", {"nochange": ""}):
        return None
    return text


def put_cargo_on_card_page(wp, card_title, update_reason="Put card query on card page", pause=False):
    page = wp.page(card_title)
    try:
        ot = page.read()
        if "{{Card Query}}" in ot:
            return
        text = card_model_1.replace_old_card_text(card_title, ot)
    except Exception:
        #TODO build new cardquery
        raise
        return
    return update_page(card_title, page, text, update_reason, ot, pause)


def put_cargo_on_new_card_page(wp, card_title, update_reason="Put card query on card page", pause=False):
    page = wp.page(card_title)
    try:
        ot = page.read()
        return
    except Exception:
        pass
    return update_page(card_title, page, "{{Card Query}}", update_reason, "", pause)


def update_reprint_with_errata(ct, errata, card):
    new_version = "Mass Mutation Mastervault"
    ct.append("ErrataData", {"Text":errata["old"], "Version":""})
    ct.append("ErrataData", {"Text":card["card_text"], "Version":"Mass Mutation"})


def update_card_page_cargo(wp, card, update_reason="", data_to_update="carddb", restricted=[], pause=True, use_csv=False):
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
        carddb.get_cargo(card, ct, restricted)
    elif data_to_update == "artist":
        card_model_1.pull_artist(card, ct, wp)
    elif data_to_update == "relink":
        # Grab text and flavor text from existing table and relink them
        print(ct.data_types)
        data = ct.get_data("CardData")
        for field in ["Text", "FlavorText"]:
            t = data[field]
            if field != "FlavorText":
                t = carddb.linking_keywords(t)
            t = carddb.link_card_titles(t, latest["card_title"])
            data[field] = t
        print(data)
        ct.update_or_create("CardData", latest["card_title"], data)
    elif data_to_update == "reprint_pull":
        # TODO - create editdata containing old cardtext if it doesn't exist as mm reprint data
        """{
                'CardData': {
                    'Desire': {'type': 'CardData', 'Name': 'Desire', 'Image': '479-053.png', 'Artist': 'Michele Giorgi', 'Text': "Keys [[Cost|cost]] +4{{Aember}}.  <p> '''Reap:''' [[Timing_Chart#Forge_a_Key|Forge a key]] at [[Cost|current cost]], reduced by 1{{Aember}} [[For each|for each]] friendly [http://archonarcana.com/Card_Gallery?traits=Sin Sin] creature.", 'Keywords': '', 'FlavorText': '', 'Power': '3', 'Armor': '0', 'Amber': '0', 'Assault': '0', 'Hazardous': '0', 'EnhanceDamage': '0', 'EnhanceAmber': '0', 'EnhanceDraw': '0', 'EnhanceCapture': '0', 'Type': 'Creature', 'House': 'Dis', 'Traits': 'Demon • Sin', 'Rarity': 'Variant'}
                }, 
                'SetData': {
                    'Mass Mutation': {'type': 'SetData', 'SetName': 'Mass Mutation', 'SetNumber': '479', 'CardNumber': '053'}
                }
            }"""
        if(ct.get_datas("CardData")[0]["Text"]!=latest["card_text"]):
            csv_changes.write(latest["card_title"]+"\n")
            csv_changes.write(ct.get_datas("CardData")[0]["Text"]+"\n")
            csv_changes.write(latest["card_text"]+"\n\n")
            csv_changes.flush()
    elif data_to_update == "reprint_write":
        errata = reprints["errata"].get(latest["card_title"], None)
        if errata:
            update_reprint_with_errata(ct, errata, latest)
        modified = reprints["edited"].get(latest["card_title"], None)
        if modified:
            ct.get_datas("CardData")[0]["Text"] = modified["new"]
        carddb.get_cargo(card, ct, [key for key in ct.get_datas("CardData")[0].keys() if key not in ["Artist"]])            
    text = ct.output_text()
    if ot==text:
        return
    if use_csv:
        csv_changes.write(latest["card_title"]+"\t"+str(latest["expansion"])+"\t"+str(latest["card_number"])+"\t"+ot.replace("\n","\r")+"\t"+text.replace("\n","\r")+"\n")
        csv_changes.flush()
        return
    return update_page(latest["card_title"], page, text, update_reason, ot, pause)


def update_cards_v2(wp, search_name=None,
                    update_reason="phase 2 test",
                    data_to_update="carddb",
                    restricted=[],
                    matching=None,
                    restrict_expansion=479,
                    upload_image=False):
    changed = 0
    started = False
    for i, card_name in enumerate(sorted(carddb.cards.keys())):
        if not started and (search_name and search_name.lower() not in card_name.lower()):
            continue
        latest = carddb.get_latest(card_name)
        if matching and matching.lower() not in (latest["flavor_text"]+latest["card_text"]).lower():
            continue
        if restrict_expansion and not latest["expansion"] == restrict_expansion:
            continue
        started = True
        print(i+1, card_name)
        if upload_image:
            rp = latest["image_number"]
            lp = "images/"+rp
            if not os.path.exists(lp):
                print("download", latest["front_image"])
                with open(lp, "wb") as f:
                    r = requests.get(latest["front_image"], stream=True)
                    print(r.status_code)
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            with open(lp, "rb") as f:
                print(wp.upload(f, latest["image_number"]))
        if data_to_update == "cargo_to_card":
            text = put_cargo_on_card_page(wp, card_name)
        if data_to_update == "cargo_to_card2":
            text = put_cargo_on_new_card_page(wp, card_name)
        else:
            text = update_card_page_cargo(
                wp, carddb.cards[card_name],
                update_reason=update_reason,
                restricted=restricted,
                data_to_update=data_to_update)
        if text:
            print("changed:", text)
            changed += 1
            time.sleep(0.05)
    print(changed, "cards changed")