import time
from models import wiki_card_db, wiki_model
import wikibase
from wikibase import update_page
import requests
import os
import shutil
import json
import re
from deepdiff import DeepDiff
from deepdiff.operator import BaseOperator
from tool_update_cards import update_card_views

with open("data/locales.json") as f:
    locales = json.loads(f.read())

class textual_diff(BaseOperator):
    def give_up_diffing(self, level, diff_instance):
        if level.t1 in [None, ""] and level.t2 in [None, ""]:
            return True
        if str(level.t1) == str(level.t2):
            return True

def read_change(wp, card, locale=None, fields=[]):
    latest_english = wiki_card_db.get_latest_from_card(card)
    latest = wiki_card_db.get_latest_from_card(card, locale)
    page = wp.page("CardData:" + latest_english["card_title"])
    print(page.title)
    ct_old = wikibase.CargoTable()
    ct_new = wikibase.CargoTable()
    ot = ""
    try:
        ot = page.read()
        ct_old.read_from_text(ot)
        ct_new.read_from_text(ot)
    except Exception:
        pass
    wiki_card_db.get_cargo(card, ct_new)
    ct_old.restrict_fields(fields)
    ct_new.restrict_fields(fields)
    diff = DeepDiff(ct_old, ct_new, custom_operators=[textual_diff(['.*'])], verbose_level=2).to_dict()
    if not diff:
        return diff
    print("\n","card:",card,"\n")
    if len(list(wiki_card_db.get_sets(card))) > 1:
        diff['reason'] = 'revision'
    else:
        diff['reason'] = 'update'
    # ensure card can be serialized, or crash the process
    if "type_changes" in diff:
        for ck in diff["type_changes"]:
            diff["type_changes"][ck]["old_type"] = repr(diff["type_changes"][ck]["old_type"])
            diff["type_changes"][ck]["new_type"] = repr(diff["type_changes"][ck]["new_type"])
            print(ck)
    print("_diff_:", diff, "\n")
    json.dumps(diff)
    return diff


def read_changes(wp, search_name=None,
                    restrict_expansion=None,
                    locale=None,
                    card_name=False,
                    fields=[]):
    limit = 3000
    changed = 0
    started = False
    search_cards = sorted(wiki_card_db.cards.keys())
    if card_name:
        search_cards = [card_name]
    found_changes = {}
    for i, card_name in enumerate(search_cards):
        if search_name and not re.findall(search_name, card_name):
            continue
        card_datas = wiki_card_db.cards[card_name]
        if restrict_expansion and not str(restrict_expansion) in [str(set_name) for set_name in card_datas]:
            continue
        started = True
        print('++ ',i+1, card_name)
        print(' + update card page cargo')
        print(len(wiki_card_db.cards[card_name]))
        diff = read_change(
            wp, card_datas,
            locale=locale,
            fields=fields
        )
        if diff:
            found_changes[card_name] = diff
            changed += 1
        if changed >= limit:
            break
    if os.path.exists("data/changed_cards.json"):
        f = open("data/changed_cards.json")
        old = json.loads(f.read())
        f.close()
        # Copy any old keys into found_changes if the reason has been modified
        for k in sorted(old):
            if old[k]['reason'] not in ['revision', 'update']:
                found_changes[k] = old[k]
    f = open(f"data/changed_cards_{restrict_expansion}.json", "w")
    f.write(json.dumps(found_changes, indent=2, sort_keys=True))
    f.close()

def write_changes(wp, filename, locale=None):
    f = open(filename)
    requested_changes = json.loads(f.read())
    f.close()
    limit = 1000
    # lint step
    valid_changes = []

    changes = 0
    for i, card_name in enumerate(requested_changes.keys()):
        page = wp.page("CardData:" + card_name)
        try:
            ot = page.read()
        except Exception:
            ot = ""
        old_table = wikibase.CargoTable()
        old_table.read_from_text(ot)
        new_table = wikibase.CargoTable()
        new_table.read_from_text(ot)


        change_requested = requested_changes[card_name]
        if change_requested["reason"] == "skip":
            continue
        elif not change_requested["reason"] in ["update", "revision", "addset"]:
            raise Exception(f"Card {card_name} has invalid reason")

        changed_fields = {}
        def apply_field(field, value):
            field = field.replace("root.data_types", "")
            subs = re.findall("\[\'(.*?)\'\]", field)
            ob = new_table.data_types
            while len(subs) > 1:
                ob = ob[subs.pop(0)]
            ob[subs[0]] = value
            changed_fields[subs[0]] = 1

        #print("BEFORE", card_name, root.data_types)
        for k in change_requested:
            if k not in ["reason", "type_changes", "values_changed", "dictionary_item_added"]:
                raise Exception(f"Card {card_name} has unknown change {k}")
            change_set = change_requested[k]
            if k == "reason": continue
            if k == "type_changes":
                for field in change_set:
                    apply_field(field, change_set[field]['new_value'])
            elif k == "values_changed":
                for field in change_set:
                    apply_field(field, change_set[field]['new_value'])
            elif k == "dictionary_item_added":
                for field in change_set:
                    apply_field(field, change_set[field])
        #print("AFTER", card_name, root.data_types)
        diff = DeepDiff(old_table, new_table, custom_operators=[textual_diff(['.*'])], verbose_level=2).to_dict()
        if diff:
            print(diff)
                
        valid_changes.append((card_name, new_table, change_requested, list(changed_fields.keys())))
        changes += 1
        if changes >= limit:
            break
    
    print(valid_changes)

    changes = 0
    for (card_name, ct, change_requested, fields) in valid_changes:
        # Simplest, just update the CardData page
        if change_requested["reason"] == "update":
            page = wp.page("CardData:" + card_name)
            try:
                ot = page.read()
            except Exception:
                ot = ""
            ot_cargo = wikibase.CargoTable()
            ot_cargo.read_from_text(ot)
            # TODO hack to copy artist field
            print(card_name)
            if ot_cargo.data_types and "Artist" in ot_cargo.data_types["CardData"][card_name]:
                ct.data_types["CardData"][card_name]["Artist"] = ot_cargo.data_types["CardData"][card_name]["Artist"]
            text = ct.output_text()
            print("view update:", update_card_views(wp, card_name, "GR mastervault pull", False, True))
            if ot == text:
                continue
            print(text)
            update_page(card_name, page, text, "GR mastervault pull", ot)
            import alerts
            # FIXME move this to wikibase or somewhere
            alerts.discord_alert(f"Updated card https://archonarcana.com/{card_name.replace(' ', '_')} with fields {fields}")
        elif change_requested["reason"] == "addset":
            page = wp.page("CardData:" + card_name)
            try:
                ot = page.read()
            except Exception:
                ot = ""
            ot_cargo = wikibase.CargoTable()
            ot_cargo.read_from_text(ot)
            text = ct.output_text()
            if ot == text:
                continue
            print(text)
            update_page(card_name, page, text, "Adding set data", ot)
            import alerts
            alerts.discord_alert(f"Updated card https://archonarcana.com/{card_name.replace(' ', '_')} with fields {fields}")
        elif change_requested["reason"] == "revision":
            page = wp.page("CardData:" + card_name)
            try:
                ot = page.read()
            except Exception:
                ot = ""
            ot_cargo = wikibase.CargoTable()
            ot_cargo.read_from_text(ot)
            text = ct.output_text()
            if ot == text:
                continue
            print(text)
            update_page(card_name, page, text, "Making revision from GR mastervault pull", ot)
            import alerts
            alerts.discord_alert(f"Updated card https://archonarcana.com/{card_name.replace(' ', '_')} with fields {fields}")
        else:
            print(f"Unknown change reason: {change_requested['reason']}")
            crash
        changes += 1
        if changes >= limit:
            break

    

def test_read_ct():
    import connections
    wp = connections.get_wiki()
    page = wp.page("CardData:CPO Zytar")
    ct_old = wikibase.CargoTable()
    ct_old.read_from_text(page.read())
    print(ct_old.data_types)
    crash
