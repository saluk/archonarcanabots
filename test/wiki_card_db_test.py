import unittest
import copy

from models import wiki_card_db
from models import skyjedi_model


class WikiCardDbTests(unittest.TestCase):

    def setUp(self):
        # unittest suggests this when test data diffs
        # were too long.
        self.maxDiff = None

        self.setUp_bifurcate()


    def setUp_bifurcate(self):
        local_json = skyjedi_model.LocalJson()
        local_json.add_file(
            "data/test_data/wiki_card_db_examples.json"
        )
        self.cards = local_json.get_cards()

        # In MM: Cre1/2, Rare/FIXED, and
        # both halves have the card text.
        self.ultra1_mm = self.find(
            "f8b21c6a-56a4-4e1e-8a4a-ca4bcb8e3b68"
        )
        self.ultra2_mm = self.find(
            "2520f79b-ad48-47ba-b96e-1b34a528ed5e"
        )
        # In MoMu: Cre/Cre, Rare/Special,
        # and only one half has the card text.
        self.ultra1_momu = self.find(
            "0afebc37-1f09-4544-9bca-d3ee05855c21"
        )
        self.ultra2_momu = self.find(
            "ef7e2d21-cb1b-413a-8f8b-bc37335d19ee"
        )

        self.grim_anomaly = self.find(
            "62427579-c56b-4665-b1a1-85c04e16ba6e"
        )
        self.grim_gr = self.find(
            "6448ac87-5019-4bfd-9a8f-021de5a7e3e3"
        )

        self.johnny_mm = self.find(
            "e955f15e-168f-4b9a-a17a-7a6191d62390"
        )
        self.johnny_toc_redem = self.find(
            "f74a8d23-d941-4aaa-8030-8eff3dc0dd64"
        )

        self.chuff_cota = self.find(
            "2948a6fc-f7fa-45f2-b73d-fdf5f4216e46"
        )
        self.chuff_mcw = self.find(
            "ed4f373a-512b-4dbc-8e99-7771fdd61ed0"
        )
        self.taengoo_mcw = self.find(
            "0051e976-e65e-48e1-9f1e-b025e281528b"
        )

        # a real example that becomes multi house
        # via JSON data? I think this case might come
        # from processing decks? I messed around with this
        # case but I don't think its triggering in skyjedi
        # JSON mode. We can always add if needed.


        # And some cards that don't need special
        # bifurcation
        self.dew_cota = self.find(
            "f0c4cb0f-8e5f-454c-a6ad-35f35ac3c98a"
        )
        self.fear_cota = self.find(
            "10715fd2-031a-47ca-9119-9b7b2ec1d2c0"
        )

        # For AA card data processing like X power.
        self.wave = self.find(
            "ac3a1d32-f21d-4336-b263-ac55817c59f6"
        )
        self.picaroon = self.find(
            "a9479b8e-710e-420f-aac4-de1d2d10aeb5"
        )
        self.archivist = self.find(
            "9a21e4ec-bedd-4494-a7d0-5bf047587ea4"
        )

    def find(self, card_id):
        for card in self.cards:
            if card["id"] == card_id:
                return card
        raise Exception("Missing id")


    def test_bifurcate_giants(self):
        # Returns (is_giant, merged_halves)
        # Returns (multi_house, merged)
        expected = (
            False,
            []
        )
        actual = wiki_card_db.bifurcate_giants(
            [self.dew_cota]
        )
        self.assertEqual(expected, actual)

        ultra_mm_merged = copy.deepcopy(self.ultra1_mm)
        ultra_mm_merged["card_type"] = "Creature"
        ultra_momu_merged = copy.deepcopy(self.ultra2_momu)
        ultra_momu_merged["rarity"] = "Rare"
        expected = (
            True,
            [ultra_mm_merged, ultra_momu_merged]
        )
        actual = wiki_card_db.bifurcate_giants(
            [self.ultra1_mm, self.ultra2_mm,
             self.ultra1_momu, self.ultra2_momu]
        )
        self.assertEqual(expected, actual)


    def test_bifurcate_anomalies(self):
        # Returns (has_anomaly, anomalies, other)
        expected = (
            False,
            [],
            [self.dew_cota]
        )
        actual = wiki_card_db.bifurcate_anomalies(
            [self.dew_cota]
        )
        self.assertEqual(expected, actual)

        expected = (
            True,
            [self.grim_anomaly],
            [self.grim_gr]
        )
        actual = wiki_card_db.bifurcate_anomalies(
            [self.grim_gr, self.grim_anomaly]
        )
        self.assertEqual(expected, actual)


    def test_bifurcate_redemption(self):
        # Returns (has_redemption, redemption, other)
        expected = (
            False,
            [],
            [self.dew_cota]
        )
        actual = wiki_card_db.bifurcate_redemption(
            [self.dew_cota]
        )
        self.assertEqual(expected, actual)

        johnny_toc_redem_updated = \
            copy.deepcopy(self.johnny_toc_redem)
        johnny_toc_redem_updated["card_title"] = \
            "Johnny Longfingers (Redemption)"
        expected = (
            True,
            [johnny_toc_redem_updated],
            [self.johnny_mm]
        )
        actual = wiki_card_db.bifurcate_redemption(
            [self.johnny_mm, self.johnny_toc_redem]
        )
        self.assertEqual(expected, actual)


    def test_bifurcate_martian_faction(self):
        # Returns (has_martian_faction, faction, other)
        expected = (
            False,
            [],
            [self.dew_cota]
        )
        actual = wiki_card_db.bifurcate_martian_faction(
            [self.dew_cota]
        )
        self.assertEqual(expected, actual)

        chuff_mcw_updated = copy.deepcopy(self.chuff_mcw)
        chuff_mcw_updated["card_title"] = "Chuff Ape (Elders)"
        expected = (
            True,
            [chuff_mcw_updated],
            [self.chuff_cota]
        )
        actual = wiki_card_db.bifurcate_martian_faction(
            [self.chuff_cota, self.chuff_mcw]
        )
        self.assertEqual(expected, actual)

        taengoo_mcw_updated = copy.deepcopy(self.taengoo_mcw)
        taengoo_mcw_updated["card_title"] = \
            "Agent Taengoo (Ironyx Rebels)"
        expected = (
            True,
            [taengoo_mcw_updated],
            []
        )
        actual = wiki_card_db.bifurcate_martian_faction(
            [self.taengoo_mcw]
        )
        self.assertEqual(expected, actual)


    def test_bifurcate_multi_house(self):
        # Returns (multi_house, merged)
        pass


    def test_process_skyjedi_card_batch(self):
        # From other tests above, get all the inputs and all
        # the expectations. Together run the whole shebang
        # here so the interactions between bifurcate functions
        # comes out correctly.

        ultra_mm_merged = copy.deepcopy(self.ultra1_mm)
        ultra_mm_merged["card_type"] = "Creature"
        ultra_mm_merged["power"] = 10
        ultra_momu_merged = copy.deepcopy(self.ultra2_momu)
        ultra_momu_merged["rarity"] = "Rare"
        ultra_momu_merged["power"] = 10

        johnny_mm_updated = \
            copy.deepcopy(self.johnny_mm)
        johnny_mm_updated["power"] = 4

        johnny_toc_redem_updated = \
            copy.deepcopy(self.johnny_toc_redem)
        johnny_toc_redem_updated["card_title"] = \
            "Johnny Longfingers (Redemption)"
        johnny_toc_redem_updated["power"] = 4

        dew_updated = copy.deepcopy(self.dew_cota)
        dew_updated["power"] = 2

        grim_anomaly_updated = copy.deepcopy(self.grim_anomaly)
        grim_anomaly_updated["power"] = 4
        grim_gr_updated = copy.deepcopy(self.grim_gr)
        grim_gr_updated["power"] = 4

        chuff_cota_updated = copy.deepcopy(self.chuff_cota)
        chuff_cota_updated["power"] = 11
        chuff_mcw_updated = copy.deepcopy(self.chuff_mcw)
        chuff_mcw_updated["card_title"] = "Chuff Ape (Elders)"
        chuff_mcw_updated["power"] = 11
        taengoo_mcw_updated = copy.deepcopy(self.taengoo_mcw)
        taengoo_mcw_updated["card_title"] = \
            "Agent Taengoo (Ironyx Rebels)"
        taengoo_mcw_updated["power"] = 1

        expected = [
            # Some single no-bifurcate cards.
            dew_updated, self.fear_cota,
            # Giants per-set merge.
            ultra_mm_merged, ultra_momu_merged,
            # Anomalies do not combine into one card.
            grim_anomaly_updated, grim_gr_updated,
            # Redemption variant becomes a new card.
            johnny_toc_redem_updated, johnny_mm_updated,
            # Original card stays the same, while MCW
            # variants become a new card. A debut MCW
            # card also starts with the suffix.
            chuff_cota_updated,
            chuff_mcw_updated, taengoo_mcw_updated,
        ]

        actual = wiki_card_db.process_skyjedi_card_batch(
            [
                self.dew_cota, self.fear_cota,
                self.ultra1_mm, self.ultra2_mm,
                self.ultra1_momu, self.ultra2_momu,
                self.grim_anomaly, self.grim_gr,
                self.johnny_mm, self.johnny_toc_redem,
                self.chuff_cota,
                self.chuff_mcw, self.taengoo_mcw,
            ]
        )

        # Ignores order of lists.
        self.assertCountEqual(expected, actual)


    def test_process_aa_card_data(self):

        # Cards without power left alone.
        wave = {
            "card_title": "Cleansing Wave",
            "power": None,
        }
        wiki_card_db.process_aa_card_data(wave)
        self.assertEqual(wave["power"], None)

        # Cards with integer power get integer.
        archivist = {
            "card_title": "The Archivist",
            "power": "3",
        }
        wiki_card_db.process_aa_card_data(archivist)
        self.assertEqual(archivist["power"], 3)

        # X-power gets turned into integer zero.
        picaroon = {
            "card_title": "Picaroon",
            "power": "X",
        }
        wiki_card_db.process_aa_card_data(picaroon)
        self.assertEqual(picaroon["power"], 0)
