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
parser.add_argument("--locale", type=str, help="The full two part locale, such as es-es. Multiple can be separated with commas.")
parser.add_argument("--images", action="store_true", help="For importing CardData, should we upload the images?")
parser.add_argument("--stage", type=str, help="dev or prod for javascript files (not in use", default="dev")
parser.add_argument("--test", action="store_true", help="For uploading script files, is this a test run")
parser.add_argument("--locale_only", action="store_true", help="when updating card pages, this will only do updates to /locale/ pages")
parser.add_argument("--testfile", type=str, help="a json of test data to load for functions that take tests")
parser.add_argument("--sheet", type=str, help="The spreadsheet name to merge")
parser.add_argument("--restrict_expansion", type=int, help="Expansion number to limit")
args = parser.parse_args()
args.pause = not args.batch
print(vars(args))

if __name__ == "__main__":
    if args.command == "import_cards":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data", 
                                            "carddb", args.restricted.split("|") if args.restricted else [],
                                            restrict_expansion=args.restrict_expansion,
                                            upload_image=args.images,
                                            pause=args.pause)
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
    if args.command == "build_wiki_db":
        from models import wiki_card_db
        wiki_card_db.build_json()
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
