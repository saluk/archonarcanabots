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

# TODO if less than 10, don't process

# TODO: a main with arg parsing that makes the call and passing JSON along

# TODO: a final thing that persists the seen card ids and the page number
# we've used so far.

# the first call doesn't include cards, so its just working off the card IDs.
# skip mavericks and legacies
# keep a 


class MVLite(object):
    def __init__(self, expansion):
        self.expansion = expansion


    # Over sessions of looking for a set's cards, how many
    # pages have we checked, and what card IDs have we found?
    def loadProgress(self, json_file):
        with open(json_file, 'r') as f:
            self.progress = json5.load(f)


    # Full card data for the set so far.
    def loadCards(self, json_file):
        with open(json_file, 'r') as f:
            self.cards = json5.load(f)


    def saveProgress(self, json_file):
        self.progress['cards_found'].sort()
        with open(json_file, 'w') as f:
            f.write(json5.dumps(self.progress))


    def saveCards(self, json_file):
        self.cards.sort(key=lambda c: c['id'])
        with open(json_file, 'w') as f:
            f.write(json5.dumps(self.cards))


    # Does the list of cards in progress match the full card
    # card data IDs?
    def checkConsistency(self):
        progIdsList = self.progress['cards_found']
        progIdsSet = set(progIdsList)

        cardIdsList = [c['id'] for c in self.cards]
        cardIdsSet = set(cardIdsList)

        if len(progIdsList) != len(progIdsSet):
            raise Exception('Duplicates in progress file')

        if len(cardIdsList) != len(cardIdsSet):
            raise Exception('Duplicates in card file')

        if progIdsSet != cardIdsSet:
            raise Exception(
                'Different IDs between progress and card file')


    # There are no fully linked cards in the first
    # request for a page of decklists. Return true
    # if a new card is seen.
    def processDecklistPage(self, apiResp):
        p = self.progress['highest_page_number']
        self.progress['highest_page_number'] = p+1
        for d in apiResp['data']:
            for c in d['cards']:
                # Legacies are from a prior set, skip.
                if c in d['set_era_cards']['Legacy']:
                    continue
                # Anomalies are in their own set, 453, skip.
                if c in d['set_era_cards']['Anomaly']:
                    continue
                if c not in self.progress['cards_found']:
                    print('New card '+c)
                    return True
        return False

    def processDecklistPageWithCards(self, apiResp):
        for c in apiResp['_linked']['cards']:
            print('   considering '+c['id'])
            # Anomalies are in their own set.
            if c['expansion'] != self.expansion:
                continue
            if c['is_anomaly']:
                continue
            # We don't want maverick version in set data.
            if c['is_maverick']:
                continue
            if c['id'] not in self.progress['cards_found']:
                print('     inserting '+c['id'])
                self.progress['cards_found'].append(c['id'])
                self.cards.append(c)


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
