import time
from models import wiki_card_db, wiki_model
import wikibase
from wikibase import update_page
import requests
import os
import shutil
import json
import re

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


with open("data/locales.json") as f:
    locales = json.loads(f.read())
def update_card_views(wp, card_title, update_reason="WoE updates", pause=False, locale_only=False, only_new_edits=False):
    print("update_card_views", card_title, pause)
    page = wp.page(card_title)
    updates = []
    if not locale_only:
        updates.append(update_page(
            card_title,
            page,
            "{{#invoke: luacard | viewcard | cardname=%(n)s}}" % {"n": card_title},
            update_reason,
            "",
            pause,
            read=True,
            only_new_edits=only_new_edits
        ))
    #langs = []
    #langs.append('<div class="translate translate-en" style="display:inline">{{#invoke: luacard | viewcard | cardname=%(n)s}}</div>' % 
    #        {"n": card_title}
    #)
    # NOTE: we dynamically generate the locale with a WP extension, don't need individual locale pages
    for locale in []: # locales:
        print("... updating", card_title, locale)
        if locale == "en": continue
        wiki_locale_short, locale_name = locales[locale][0]
        page_link = card_title+'/locale/'+wiki_locale_short
        page = wp.page(page_link)
        updates.append(update_page(
            page_link,
            page,
            '{{#invoke: luacard | viewcard | cardname=%s | locale=%s}}' % 
                (card_title, locale),
            update_reason,
            "",
            pause=pause,
            read=True,
            only_new_edits=only_new_edits
            )
        )
        if updates[-1]:
            time.sleep(2)
        #langs.append('<div class="translate translate-%(ls)s" style="display:none">{{#invoke: luacard | viewcard | cardname=%(n)s | locale=%(l)s}}</div>' % 
        #        {"n": card_title, "l": locale, "ls": wiki_locale_short}
        #)
    #updates.append(update_page(card_title, page, "\n".join(langs), update_reason, "", pause=pause))
    return updates


def update_reprint_with_errata(ct, errata, card):
    new_version = "Mass Mutation Mastervault"
    ct.append("ErrataData", {"Text":errata["old"], "Version":""})
    ct.append("ErrataData", {"Text":card["card_text"], "Version":"Mass Mutation"})


def update_card_page_cargo(wp, card, update_reason="", data_to_update="carddb", restricted=[], pause=True, use_csv=False,
        only_sets=False,
        locale=None,
        only_new_edits=False
    ):
    latest_english = wiki_card_db.get_latest_from_card(card)
    latest = wiki_card_db.get_latest_from_card(card, locale)
    print(latest)
    print(latest_english)
    page = wp.page("CardData:" + latest_english["card_title"] + ("-Locale" if locale else ""))
    print(page.title)
    ct = wikibase.CargoTable()
    ot = ""
    try:
        ot = page.read()
        ct.read_from_text(page.read())
        if ct and only_new_edits:
            return
    except Exception:
        pass
    print(ct.data_types)
    if data_to_update == "carddb":
        if locale:
            wiki_card_db.get_cargo_locale(card, ct, 
                locale=locale, english_name=latest_english["card_title"])
            print(ct.data_types)
        else:
            wiki_card_db.get_cargo(card, ct, restricted, only_sets, locale=locale)
    elif data_to_update == "insert_search_text":
        wiki_card_db.get_cargo(card, ct, ["SearchText", "SearchFlavorText"])
    elif data_to_update == "relink":
        # Grab text and flavor text from existing table and relink them
        print(ct.data_types)
        data = ct.get_data("CardData")
        for field in ["Text", "FlavorText"]:
            t = data[field]
            if field != "FlavorText":
                t = wiki_model.linking_keywords(t)
            t = wiki_card_db.link_card_titles(t, latest["card_title"])
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
        wiki_card_db.get_cargo(card, ct, [key for key in ct.get_datas("CardData")[0].keys() if key not in ["Artist"]])     
    text = ct.output_text()
    print("--------\n",text,"\n--------")
    if ot==text:
        return
    if use_csv:
        csv_changes.write(latest["card_title"]+"\t"+str(latest["expansion"])+"\t"+str(latest["card_number"])+"\t"+ot.replace("\n","\r")+"\t"+text.replace("\n","\r")+"\n")
        csv_changes.flush()
        return
    return update_page(latest["card_title"], page, text, update_reason, ot, pause)


def upload_image_for_card(wp, locale, card):
    #Don't bother uploading localized images if the image is in english
    if locale and "/en/" in card["front_image"]:
        return False
    else:
        rp = card["image_number"]
        lp = "images/"+rp
        print("image path",lp)
        if not os.path.exists(lp):
            print("download", card["front_image"])
            with open(lp, "wb") as f:
                front_image = card["front_image"].replace("cdn.keyforgegame.com", "mastervault-storage-prod.s3.amazonaws.com")
                r = requests.get(card["front_image"], stream=True)
                print(r.status_code)
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        with open(lp, "rb") as f:
            print("uploading")
            try:
                result = wp.upload(f, card["image_number"])
            except Exception:
                print("Exception uploading image ",card["image_number"])
                return False
            print(result)
            if result.get('upload',{}).get('result','') == "Warning":
                return False
            return result


def update_cards_v2(wp, search_name=None,
                    update_reason="phase 2 test",
                    data_to_update="carddb",
                    restricted=[],
                    matching=None,
                    restrict_expansion=None,
                    upload_image=False,
                    locale=None,
                    locale_only=False,
                    pause=True,
                    card_name=False,
                    only_new_edits=False):
    changed = 0
    started = False
    search_cards = sorted(wiki_card_db.cards.keys())
    if card_name:
        search_cards = [card_name]
    print("\n\n ++ Update cards: Start search")
    for i, card_name in enumerate(search_cards):
        if search_name and not re.findall(search_name, card_name):
            continue
        latest = wiki_card_db.get_latest(card_name, locale=locale)
        if matching and matching.lower() not in (latest["flavor_text"]+latest["card_text"]).lower():
            continue
        if restrict_expansion and not latest["expansion"] == restrict_expansion:
            continue
        started = True
        print('++ ',i+1, card_name)
        #print(latest)
        texts = []
        if upload_image:
            print(' + upload image for card')
            texts.append(upload_image_for_card(wp, locale, latest))
        if data_to_update == "update_card_views":
            print(' + update card views')
            texts.extend(update_card_views(wp, card_name, pause=pause, locale_only=locale_only, only_new_edits=only_new_edits))
        else:
            print(' + update card page cargo')
            texts.append(update_card_page_cargo(
                wp, wiki_card_db.cards[card_name],
                update_reason=update_reason,
                restricted=restricted,
                data_to_update=data_to_update,
                locale=locale,
                pause=pause,
                only_new_edits=only_new_edits))
        texts = texts or []
        wait = False
        for text in texts:
            if text:
                wait = True
                print("changed:", text)
                changed += 1
        if texts[0]:
            import alerts
            alerts.discord_alert("Updated card %s with fields %s." % (
                'https://archonarcana.com/%s' % (card_name.replace(" ","_")),
                restricted or "ALL",
            ))
        if wait:
            time.sleep(0.05)
    print(changed, "cards changed")
    return changed

def show_cards_with_extra(wp):
    import re
    extras = {}
    for i, card_name in enumerate(sorted(wiki_card_db.cards.keys())):
        page = wp.page(card_name)
        text = page.read()
        extra = re.sub("{{Card Query.*?}}", "", text).strip()
        if extra:
            extras[card_name] = extra
    for card_name in extras:
        print("== "+card_name+" ==")
        print(extras[card_name])
        print("")
    print(len(extras))
