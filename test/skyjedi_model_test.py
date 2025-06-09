import unittest

from models import skyjedi_model


class SkyjediModelTests(unittest.TestCase):

    def test_skybeast_all_houses(self):
        local_json = skyjedi_model.LocalJson()
        local_json.add_file(
            "data/test_data/skyjedi_aes_examples.json"
        )
        cards = local_json.get_cards()

        drx = None
        drake = None
        for c in cards:
            if c["card_title"] == "Dr. Xyloxxzlphrex":
                if drx:
                    self.assertTrue(False)
                else:
                    drx = c
            if c["card_title"] == "Yellow Æmberdrake":
                if drake:
                    self.assertTrue(False)
                else:
                    drake = c

        # Leave other cards unmodified.
        self.assertEqual(drx["house"], "Mars")

        # Update cards that need extra info.
        self.assertEqual(
            drake["house"],
            "Brobnar • Dis • Ekwidon • Geistoid • Logos • Mars • Skyborn"
        )
