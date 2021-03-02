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
parser.add_argument("--restricted", type=str)
parser.add_argument("--locale", type=str, help="The full two part locale, such as es-es")
parser.add_argument("--stage", type=str, help="dev or prod for javascript files (not in use", default="dev")
parser.add_argument("--test", action="store_true", help="For uploading script files, is this a test run")
parser.add_argument("--locale_only", action="store_true", help="when updating card pages, this will only do updates to /locale/ pages")
args = parser.parse_args()
args.pause = not args.batch
print(vars(args))

if __name__ == "__main__":
    if args.command == "import_cards":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data (mm)", 
                                            "carddb", args.restricted.split("|") if args.restricted else [],
                                            upload_image=False)
    if args.command == "import_cards_locale":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data locale="+args.locale, 
                                            "carddb", [],
                                            upload_image=True,
                                            locale=args.locale,
                                            pause=args.pause)
    if args.command == "reprint_pull":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data (mm reprints)", 
                                            "reprint_pull")
    if args.command == "reprint_write":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "importing card data (mm reprints)", 
                                            "reprint_write")
    if args.command == "insert_search_text":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "inserting search text", 
                                            "insert_search_text")
    if args.command == "update_card_views":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, args.search, "put card query on card", "update_card_views", 
            locale_only=args.locale_only, pause=args.pause)
    if args.command == "relink":
        import tool_update_cards
        tool_update_cards.update_cards_v2(wp, None, "relink card data", "relink", matching=args.search)
    if args.command == "javascript":
        from javascript import upload
        upload.upload(args.stage, args.test)
    if args.command == "lua":
        from scribunto import upload
        upload.upload(args.test)
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
    if args.command == "merge_translate_spreadsheet":
        import tool_merge_db
        tool_merge_db.merge(wp, "up")
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