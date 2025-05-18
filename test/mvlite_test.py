# We're only testing some of the key functions of
# mvlite. We skip the outer logic that makes actual
# requests and also skip the check that each page
# has the max of 10 decks.

# In the test data we already have card 'bb' and
# we're looking to find 'aa' through 'ee', but
# skip 'xx' and 'jj' which are legacies.
# Pages 1 and 2 have new cards to find.
# Page 3 has only cards we've already seen.

import unittest
import json5

from mastervault import mvlite


class MVLiteTests(unittest.TestCase):

    def open_json(self, json_file):
        with open(json_file, 'r') as f:
            return json5.load(f)

    def setupCheckConsistency(self, progFile, cardFile):
        mvl = mvlite.MVLite(907)
        mvl.loadProgress('data/test_data/'+progFile)
        mvl.loadCards('data/test_data/'+cardFile)
        mvl.checkConsistency()

    def test_inconsistencies(self):
        # The valid progress and card files should
        # pass consistency checks.
        self.setupCheckConsistency(
            'mvlite_progress.json',
            'mvlite_cards.json'
        )

        with self.assertRaises(Exception):
            self.setupCheckConsistency(
                'mvlite_invalid_progress_duplicate.json',
                'mvlite_cards.json'
            )

        with self.assertRaises(Exception):
            self.setupCheckConsistency(
                'mvlite_invalid_progress_extra.json',
                'mvlite_cards.json'
            )
        with self.assertRaises(Exception):
            self.setupCheckConsistency(
                'mvlite_invalid_cards_duplicate.json',
                'mvlite_cards.json'
            )
        with self.assertRaises(Exception):
            self.setupCheckConsistency(
                'mvlite_invalid_cards_missing.json',
                'mvlite_cards.json'
            )

    def test_successful_three_pages(self):
        expectedFinalProgress = self.open_json(
            'data/test_data/mvlite_expected_progress.json')
        expectedFinalCards = self.open_json(
            'data/test_data/mvlite_expected_cards.json')

        mvl = mvlite.MVLite(907)

        # Load starting points
        mvl.loadProgress('data/test_data/mvlite_progress.json')
        mvl.loadCards('data/test_data/mvlite_cards.json')

        mvl.checkConsistency()

        # Page 1 has some new cards.
        print('Page 1')
        print(mvl.progress)
        pg1Resp = self.open_json(
            'data/test_data/mvlite_pg1.json')
        sawNewCard = mvl.processDecklistPage(pg1Resp)
        self.assertEqual(sawNewCard, True)

        pg1wCardsResp = self.open_json(
            'data/test_data/mvlite_pg1_w_cards.json')
        mvl.processDecklistPageWithCards(pg1wCardsResp)
        mvl.completePage()

        # Page 2 has some new cards.
        print('Page 2')
        print(mvl.progress)
        pg2Resp = self.open_json(
            'data/test_data/mvlite_pg2.json')
        sawNewCard = mvl.processDecklistPage(pg2Resp)
        self.assertEqual(sawNewCard, True)

        pg2wCardsResp = self.open_json(
            'data/test_data/mvlite_pg2_w_cards.json')
        mvl.processDecklistPageWithCards(pg2wCardsResp)
        mvl.completePage()

        # No new cards in page 3.
        print('Page 3')
        print(mvl.progress)
        pg3Resp = self.open_json(
            'data/test_data/mvlite_pg3.json')
        sawNewCard = mvl.processDecklistPage(pg3Resp)
        self.assertEqual(sawNewCard, False)
        mvl.completePage()

        # Final JSON should be sorted. Have mvlite save it and
        # then reload to compare.
        mvl.saveProgress('/tmp/p.json')
        mvl.saveCards('/tmp/c.json')

        actualFinalProgress = self.open_json('/tmp/p.json')
        actualFinalCards = self.open_json('/tmp/c.json')

        self.assertDictEqual(
            actualFinalProgress, expectedFinalProgress)
        self.assertEqual(
            actualFinalCards, expectedFinalCards)
