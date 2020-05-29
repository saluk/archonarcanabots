#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import connections

# TODO - add templates to appropriate pages
# TODO - create artist pages that list their cards

wp = connections.get_wiki()


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        print("python wiki_page_updater import_cards2 TimeTraveller")
    else:
        if sys.argv[1] == "import_cards2":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) >= 3 else None
            restricted = sys.argv[3] if len(sys.argv) >= 4 else ""
            tool_update_cards.update_cards_v2(wp, search, "importing card data (mm)", 
                                              "carddb", restricted.split("|") if restricted else [],
                                              upload_image=False)
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
        if sys.argv[1] == "import_artist":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) == 3 else None
            tool_update_cards.update_cards_v2(wp, search, "pulling artist", "artist")
        if sys.argv[1] == "cargo_to_card":
            import tool_update_cards
            search = sys.argv[2] if len(sys.argv) == 3 else None
            tool_update_cards.update_cards_v2(wp, search, "put card query on card", "cargo_to_card")
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
            upload.upload()
