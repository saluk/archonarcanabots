#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import connections
import wikibase

# TODO - add templates to appropriate pages
# TODO - create artist pages that list their cards

wp = connections.get_wiki()
mwm = wikibase.MediawikiManager(wp)

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        print("python wiki_page_updater import_cards2 TimeTraveller")
    else:
        if sys.argv[1] == "import_cards":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) >= 3 else None
            restricted = sys.argv[3] if len(sys.argv) >= 4 else ""
            tool_update_cards.update_cards_v2(wp, search, "importing card data (mm)", 
                                              "carddb", restricted.split("|") if restricted else [],
                                              upload_image=False)
        if sys.argv[1] == "import_cards_locale":
            import tool_update_cards
            locale = sys.argv[2]
            tool_update_cards.update_cards_v2(wp, "", "importing card data locale="+locale, 
                                              "carddb", [],
                                              upload_image=True,
                                              locale=locale)
        if sys.argv[1] == "reprint_pull":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) >= 3 else None
            tool_update_cards.update_cards_v2(wp, search, "importing card data (mm reprints)", 
                                              "reprint_pull")
        if sys.argv[1] == "reprint_write":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) >= 3 else None
            tool_update_cards.update_cards_v2(wp, search, "importing card data (mm reprints)", 
                                              "reprint_write")
        if sys.argv[1] == "insert_search_text":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) >= 3 else None
            tool_update_cards.update_cards_v2(wp, search, "inserting search text", 
                                              "insert_search_text")
        if sys.argv[1] == "cargo_to_card2":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) == 3 else None
            tool_update_cards.update_cards_v2(wp, search, "put card query on card", "cargo_to_card2")
        if sys.argv[1] == "relink":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) == 3 else None
            tool_update_cards.update_cards_v2(wp, None, "relink card data", "relink", matching=search)
        if sys.argv[1] == "javascript":
            from javascript import upload
            stage = sys.argv[2] if len(sys.argv) > 2 else "dev"
            test = sys.argv[3] if len(sys.argv) > 3 else None
            upload.upload(stage, test)
        if sys.argv[1] == "lua":
            from scribunto import upload
            test = sys.argv[2] if len(sys.argv) > 2 else None
            upload.upload(test)
        if sys.argv[1] == "delete":
            for page in wp.allpages(limit=500, namespace=3006):
                page.delete('Removing all deck pages')
        if sys.argv[1] == "eventdecks":
            import tool_update_decks
            tool_update_decks.update_event_decks(wp)
        if sys.argv[1] == "table_to_cargo":
            import tool_read_tables
            tool_read_tables.write(mwm)
        if sys.argv[1] == "debut_sets":
            import tool_update_cards
            tool_update_cards.update_cards_v2(wp, None, "Adding debut to debut set", "carddb", ["SetData.Meta"])