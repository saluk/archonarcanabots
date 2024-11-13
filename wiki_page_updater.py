#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import connections
import wikibase
import argparse

# TODO - add templates to appropriate pages
# TODO - create artist pages that list their cards

# Monkeypatch to add a set_page_language to wiki pages
import mw_api_client
def set_page_language(self, lang):
    return self.wiki.post_request(**{
        'action': 'setpagelanguage',
        'title': self.title,
        'token': self.wiki.meta.tokens(),
        'lang': lang
    })
mw_api_client.page.Page.set_page_language = set_page_language

wp = connections.get_wiki()

mwm = wikibase.MediawikiManager(wp)

parser = argparse.ArgumentParser(description="A swiss army knife of tools to work with data on Archon Arcana")
parser.add_argument("command", metavar="command", type=str)
parser.add_argument("--batch", action="store_true")
parser.add_argument("--search", type=str)
parser.add_argument("--restricted", type=str, help="The only card fields to update")
parser.add_argument("--excluded", type=str, help="Card fields to exclude")
parser.add_argument("--locale", type=str, help="The full two part locale, such as es-es. Multiple can be separated with commas.")
parser.add_argument("--stage", type=str, help="dev or prod for javascript files (not in use", default="dev")
parser.add_argument("--test", action="store_true", help="For uploading script files, is this a test run")
parser.add_argument("--locale_only", action="store_true", help="when updating card pages, this will only do updates to /locale/ pages")
parser.add_argument("--testfile", type=str, help="a json of test data to load for functions that take tests")
parser.add_argument("--sheet", type=str, help="The spreadsheet name to merge")
parser.add_argument("--restrict_expansion", type=int, help="Expansion number to limit")
parser.add_argument("--build_locales", type=bool, help="Whether or not to build locales when building the wiki db", default=False)
parser.add_argument("--prevent_spoilers", action="store_true", help="When prepping a spoilered set to become main, force card pages to non-spoiler values", default=False)
parser.add_argument("--change_comment", type=str, help="To annotate wiki updates.", default="bot update")
args = parser.parse_args()
args.pause = not args.batch
print(vars(args))


if __name__ == "__main__":
    # STEP 1 Run this first to update our json files from what was recorded from the mastervault in the postgresql db
    if args.command == "build_wiki_db":
        from models import wiki_card_db
        wiki_card_db.build_json(build_locales=args.build_locales)
    if args.command == "build_wiki_db_skyjedi":
        from models import wiki_card_db
        wiki_card_db.build_json(build_locales=args.build_locales, from_skyjedi=True)
    # STEP 2 Upload the new images
    if args.command == "upload_images":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "uploading image", 
                                            "carddb", [],
                                            restrict_expansion=args.restrict_expansion,
                                            upload_image=True,
                                            pause=False)
    # STEP 3 Use this command to create a json file of card changes from the mastervault
    if args.command == "read_card_changes":
        if args.restrict_expansion:
            import tool_change_cards_json
            tool_change_cards_json.read_changes(
                wp, args.search, 
                restrict_expansion=args.restrict_expansion,
                fields=args.restricted.split("|") if args.restricted else [],
                exclude_fields=args.excluded.split("|") if args.excluded else [],
                prevent_spoilers=args.prevent_spoilers
            )
        else:
            print("""You must restrict the expansion. The changes will be in terms of updating
            the database in the context of a given expansion, where updates for the current
            set are determined to be updates to spoiler data, and updates to cards
            that were previously in other sets will be made into card revisions.""")

    # STEP 4 After editing the json changes file, use this command to write the changes to the database
    if args.command == "write_card_changes":
        import tool_change_cards_json
        tool_change_cards_json.write_changes(
            wp,
            f'data/changed_cards_{args.restrict_expansion}.json',
            change_comment=args.change_comment
        )
    if args.command == "import_cards_locale":
        import tool_update_cards
        for locale in args.locale.split(","):
            tool_update_cards.update_cards_v2(wp, args.search, "importing card data locale="+args.locale, 
                                                "carddb", [],
                                                upload_image=args.images,
                                                locale=locale,
                                                pause=args.pause)
    if args.command == "reprint_pull":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data (dt reprints)", 
                                            "reprint_pull", restrict_expansion=496)
    if args.command == "reprint_write":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data (dt reprints)", 
                                            "reprint_write", restrict_expansion=496)
    if args.command == "insert_search_text":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "inserting search text", 
                                            "insert_search_text")
    if args.command == "update_card_views":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "put card query on card", "update_card_views", 
            restrict_expansion=args.restrict_expansion,
            locale_only=args.locale_only, pause=args.pause)
    if args.command == "relink":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, None, "relink card data", "relink", matching=args.search)
    if args.command == "javascript":
        from javascript import upload
        upload.upload(args.stage, args.test)
    if args.command == "lua":
        from scribunto import upload
        upload.upload(args.test, args.stage)
    if args.command == "delete":
        for page in wp.allpages(limit=500, namespace=3006):
            page.delete('Removing all deck pages')
    if args.command == "eventdecks":
        import tool_update_decks
        tool_update_decks.update_event_decks(wp)
    if args.command == "table_to_cargo":
        import tool_read_tables
        tool_read_tables.write(mwm)
    if args.command == "debut_sets":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, None, "Adding debut to debut set", "carddb", ["SetData.Meta"])
    if args.command == "merge_spreadsheets":
        import tool_merge_db
        tool_merge_db.merge(wp, args.sheet, pause=args.pause)
    if args.command == "get_cards_with_extra":
        # Gets cards that have extra content in their wikipage besides DB content
        import tool_update_cards
        tool_update_cards.show_cards_with_extra(wp)
    if args.command == "translate_traits":
        from models import wiki_card_db
        wiki_card_db.translate_all_traits()
    if args.command == "new_cards":
        from mastervault.mastervault_workers import Workers
        w = Workers()
        cards = None
        from models import mv_model
        if args.testfile:
            import json
            cards = []
            with open(args.testfile) as f:
                for card_data in json.loads(f.read()):
                    cards.append(mv_model.Card(
                        key=card_data["id"], 
                        deck_expansion=card_data["deck_expansion"],
                        name=card_data["card_title"],
                        data=card_data))
        if args.search:
            session = mv_model.Session()
            query = session.query(mv_model.Card).filter(mv_model.Card.name.like(args.search))
            cards = query.all()
            print(f"search found cards {len(cards)}")

        w.new_cards(cards, savedb=True)
        #w.new_cards(cards, savedb=True, only_new_edits=False)
    if args.command == "deck_scrape_lag":
        from mastervault.mastervault_workers import Workers
        w = Workers()
        w.deck_scrape_lag()
    if args.command == "find_no_image":
        from models import wiki_card_db
        for locale in wiki_card_db.locales:
            for card_name in wiki_card_db.locales[locale]:
                if wiki_card_db.locales[locale][card_name]['front_image'].find('/en/') >= 0:
                    print(locale, card_name, wiki_card_db.locales[locale][card_name]['front_image'])
    if args.command == "update_anomaly_sets":
        # TODO 
        # select distinct(name) from cards where deck_expansion=(set to fix) and data->>'expansion'='453' order by name;
        # ensure each of the (Anomaly) cards for this name are in the given set
        # ensure other (Anomaly) cards are NOT in the given set
        pass
    if args.command == "vm2024":
        # Read csv file, parsing set number and card name from cards that are known to be in VM 2024 set
        import csv
        from wikibase import MediawikiManager, CargoTable, update_page
        mwm = MediawikiManager(wp)
        with open("data/VM2024 Cards - List.csv") as f:
            rows = [row for row in csv.reader(f, delimiter=',',quotechar='"')]
        for row in rows[1:]:
            number, cardname = row[:2]
            if not cardname:
                continue
            pagename = "CardData:"+cardname
            print("read page:",pagename)
            # Read current card data from website
            success = False
            tries = 0
            for i in range(10):
                try:
                    text = mwm.read_page(pagename)
                    success = True
                except:
                    if "Bautrem" in pagename and "Lion" in pagename:
                        pagename = 'CardData:“Lion”_Bautrem'
                    elif '"' in pagename:
                        pagename = pagename.replace('"', '“', 1).replace('"', '”', 1)
                    else:
                        pagename = pagename.replace("'","’")
            if not success:
                crash
            ct = CargoTable(pagename)
            ct.read_from_text(text)
            print(ct.data_types)
            # Inject new set data into card data
            ct.data_types['SetData']['Vault Masters 2024'] = {'SetName': 'Vault Masters 2024', 'CardNumber':str(number), 'Meta': '', }
            new_text = ct.output_text()
            print(text)
            # Write card data into website
            change = update_page(pagename, wp.page(pagename), new_text, "Adding Vault Masters 2024", text)
            if change:
                import alerts
                alerts.discord_alert(f"Updated card https://archonarcana.com/{pagename.replace(' ','_')} with Vault Master 2024")

    if args.command == "list_cards":
        if args.restrict_expansion:
            import tool_change_cards_json
            tool_change_cards_json.list_cards(
                restrict_expansion=args.restrict_expansion
            )
        else:
            print("You must restrict the expansion.")
