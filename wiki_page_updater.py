#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import connections
import tool_update_cards

# TODO - add templates to appropriate pages
# TODO - create artist pages that list their cards

wp = connections.get_wiki()


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        print("python wiki_page_updater import_cards2 TimeTraveller")
    else:
        if sys.argv[1] == "import_cards2":
            search = sys.argv[2] if len(sys.argv) == 3 else None
            tool_update_cards.update_cards_v2(wp, search)