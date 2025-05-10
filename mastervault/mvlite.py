# MV "lite" focuses on finding the complete JSON for a new
# set of cards. It's not trying to scrape all decks or keep
# any deck information.
#
# Offline:
#   - json with the highest page number we've checked
#     and the current set of card IDs we've found.
#   - json card file of cards we've pulled so far, like
#     SkyJedi json dumps.
#
# Per-request: page by page starting from the stable oldest
# maximum page of 10 decks for the expansion, compare card
# IDs to the current found set. If a page has new cards we
# haven't seen, re-request the page with links=cards param
# to get them. After the request update the offline json
# to increment the page number we've checked, the card IDs
# we've found, and the running json card file.
# Note: if a page returns less than the max of 10, stop. This
# is a partial page and we don't want to process it until
# those next 10 are scanned.
#
#
# Tool param: Picking up from where we've left off, how many
# pages to try next?

import requests
import json5

# TODO: a main with arg parsing that makes the call and passing JSON along

# TODO: a final thing that persists the seen card ids and the page number
# we've used so far.

# the first call doesn't include cards, so its just working off the card IDs.
# skip mavericks and legacies
# keep a 

def find_card_ids():
    url = 'https://www.keyforgegame.com/api/decks'
    params = {
        'page': 1,
        'page_size': 10,  # 10 is apparent max
        'ordering': 'date',
        'expansion': 907,
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print('Non-OK response %d' % resp.status_code)
        return
    decks = json5.loads(resp.text)
    print('Found %d decks' % len(decks['data']))


if __name__ == "__main__":
    find_card_ids()
