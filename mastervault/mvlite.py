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
# NOTE! We track both card number and card ID, because
# cards with enhancements have distinct IDs. But it's still
# useful because we can skip requesting the full card data
# when we've already seen every ID in a batch.
#
# Usage
# python -m mastervault.mvlite --expansion=907 --pages=2

import argparse
import requests
import json5
import json
import time


parser = argparse.ArgumentParser(
    description='A MasterVault "lite" scraper that gathers '
    + 'cards for a set and minimizes server load.')
parser.add_argument(
    '--expansion',
    required=True,
    type=int,
    help='Set to build card data for.')
parser.add_argument(
    '--pages',
    type=int,
    default=1,
    help='How many API deck pages to attempt in this run.')


class MVLite(object):
    def __init__(self, expansion):
        self.expansion = expansion

    # Over sessions of looking for a set's cards, how many
    # pages have we checked, and what card IDs have we found?
    def loadProgress(self, json_file):
        try:
            with open(json_file, 'r') as f:
                self.progress = json5.load(f)
        except FileNotFoundError:
            self.progress = {
                'card_ids_found': [],
                'card_numbers_found': [],
                'highest_page_number': 0
            }

    # Full card data for the set so far.
    def loadCards(self, json_file):
        try:
            with open(json_file, 'r') as f:
                self.cards = json5.load(f)
        except FileNotFoundError:
            self.cards = []

    def saveProgress(self, json_file):
        self.progress['card_ids_found'].sort()
        self.progress['card_numbers_found'].sort()
        with open(json_file, 'w+') as f:
            json.dump(self.progress, f, indent=2)

    def saveCards(self, json_file):
        self.cards.sort(key=lambda c: c['card_number'])
        with open(json_file, 'w+') as f:
            json.dump(self.cards, f, indent=2)

    # Does the list of card numbers in progress match the full card
    # card data?
    def checkConsistency(self):
        progNumList = self.progress['card_numbers_found']
        progNumSet = set(progNumList)

        cardNumList = [
            '%d-%s' % (c['expansion'], c['card_number'])
            for c in self.cards
        ]
        cardNumSet = set(cardNumList)

        if len(progNumList) != len(progNumSet):
            raise Exception('Duplicates in progress file')

        if len(cardNumList) != len(cardNumSet):
            raise Exception('Duplicates in card file')

        if progNumSet != cardNumSet:
            raise Exception(
                'Different IDs between progress and card file')


    # There are no fully linked cards in the first
    # request for a page of decklists. Return true
    # if a new card ID is seen.
    def processDecklistPage(self, apiResp):
        for d in apiResp['data']:
            for c in d['cards']:
                # Legacies are from a prior set, skip.
                if c in d['set_era_cards']['Legacy']:
                    continue
                # Anomalies are in their own set, 453, skip.
                if c in d['set_era_cards']['Anomaly']:
                    continue
                if c not in self.progress['card_ids_found']:
                    print('  Found new cards')
                    return True
        return False

    def processDecklistPageWithCards(self, apiResp):
        for c in apiResp['_linked']['cards']:
            # Anomalies are in their own set.
            if c['expansion'] != self.expansion:
                continue
            if c['is_anomaly']:
                continue
            # We don't want maverick version in set data.
            if c['is_maverick']:
                continue
            # Record every ID including enhancement variations.
            # We can skip decks where we've seen them all.
            if c['id'] not in self.progress['card_ids_found']:
                self.progress['card_ids_found'].append(c['id'])
            # And then only add a card to our set if we find
            # a new unenhanced one.
            cno = '%d-%s' % (c['expansion'], c['card_number'])
            if not c['is_enhanced'] and \
               cno not in self.progress['card_numbers_found']:
                self.progress['card_numbers_found'].append(cno)
                self.cards.append(c)

    def completePage(self):
        p = self.progress['highest_page_number']
        self.progress['highest_page_number'] = p+1
        return self.progress['highest_page_number']

    def makeNextRequest(self, withCards=False):
        if not withCards:
            print(
                'Fetching page %d' %
                (self.progress['highest_page_number']+1)
            )

        url = 'https://www.keyforgegame.com/api/decks'
        params = {
            'page': self.progress['highest_page_number']+1,
            'page_size': 10,  # 10 is apparent max
            'ordering': 'date', # Start from oldest
            'expansion': self.expansion,
        }
        if withCards:
            params['links'] = 'cards'

        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            raise Exception(
                'Non-OK response %d' % resp.status_code
            )
        return json5.loads(resp.text)


if __name__ == "__main__":
    args = parser.parse_args()

    progressFile = \
        'data/mvlite_progress_%s.json' % args.expansion
    cardFile = 'data/mvlite_cards_%s.json' % args.expansion

    mvl = MVLite(args.expansion)
    mvl.loadProgress(progressFile)
    mvl.loadCards(cardFile)
    mvl.checkConsistency()

    for i in range(args.pages):
        resp = mvl.makeNextRequest(withCards=False)
        if len(resp['data']) < 10:
            print('Latest page is still partial.')
            break

        # Any new non-anomaly, etc cards in this page?
        if(mvl.processDecklistPage(resp)):
            time.sleep(6)
            resp = mvl.makeNextRequest(withCards=True)
            mvl.processDecklistPageWithCards(resp)

        print('Page %d complete.' % mvl.completePage())

        time.sleep(6)

    print('Overall, %d cards found.' % len(mvl.cards))
    mvl.checkConsistency()
    mvl.saveProgress(progressFile)
    mvl.saveCards(cardFile)
