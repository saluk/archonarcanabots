# We're only testing some of the key functions of
# mvlite. We skip the outer logic that makes actual
# requests and also skip the check that each page
# has the max of 10 decks.

# In the test data we already have card 'bb' and
# we're looking to find 'aa' through 'ee', but
# skip 'xx' and 'jj' which are legacies.
# Pages 1 and 2 have new cards to find.
# Page 3 has only cards we've seen.

import unittest

from mastervault import mvlite


class MVLiteTests(unittest.TestCase):

    def test_mvlite(self):
        expectedFinalProgress = loads('data/test_data/mvlite_expected_progress_907.json')
        expectedFinalCards = loads('data/test_data/mvlite_expected_cards_907.json')


        mvl = mvlite.MVLite()

        # Load starting points
        mvl.loadProgress('data/test_data/mvlite_progress_907.json')
        mvl.loadCards('data/test_data/mvlite_cards_907.json')

        # Page 1 has some new cards.
        pg1Resp = loads('data/test_data/mvlite_pg1.json')
        pg1wCardsResp = loads('data/test_data/mvlite_pg1_w_cards.json')

        # Page 2 has some new cards.
        pg2Resp = loads('data/test_data/mvlite_pg2.json')
        pg2wCardsResp = loads('data/test_data/mvlite_pg2_w_cards.json')

        # No new cards in page 3.
        pg3Resp = loads('data/test_data/mvlite_pg3.json')


        # Final JSON should be sorted. Have mvlite save it and
        # then reload to compare.
        self.assertEqual(mvl.saveProgress(), expectedFinalProgress)
        self.assertEqual(mvl.saveCards(), expectedFinalCards)
