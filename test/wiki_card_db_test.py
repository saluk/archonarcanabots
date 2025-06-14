import unittest
import copy

from models import wiki_card_db
from models import skyjedi_model


class WikiCardDbTests(unittest.TestCase):

    def setUp(self):
        # unittest suggests this when test data diffs
        # were too long.
        self.maxDiff = None

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

        # Prophecies and Archon Powers just get some
        # schema manipulation.
        self.heads = self.find(
            "55c0bed1-320e-4024-811b-b3f1005e385a"
        )
        self.chari = self.find(
            "70bd430f-6bd4-46bf-a041-c54647886c3c"
        )

        # Agamignus is a Redemption card that is new
        # and debuts in Redemption. It should not have
        # the "Agamignus (Redemption)" title modification.
        self.agami = self.find(
            "e0e33161-59f5-407c-83c9-e90f2efee752"
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
        # Returns (has_mixed_redemption, redemption, other)
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

        expected = (
            False,
            [],
            [copy.deepcopy(self.agami)]
        )
        actual = wiki_card_db.bifurcate_redemption(
            [self.agami]
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


    def test_bifurcate_38s(self):
        # Returns (has_38s, the38s, other)

        # First a card left untouched.
        expected = (
            False,
            [],
            [self.dew_cota]
        )
        actual = wiki_card_db.bifurcate_38s(
            [self.dew_cota]
        )
        self.assertEqual(expected, actual)

        # Next a prophecy.
        heads_updated = copy.deepcopy(self.heads)
        heads_updated["house"] = None
        heads_updated["card_type"] = "38th Card"
        expected = (
            True,
            [heads_updated],
            []
        )
        actual = wiki_card_db.bifurcate_38s(
            [self.heads]
        )
        self.assertEqual(expected, actual)

        # And an Archon Power.
        chari_updated = copy.deepcopy(self.chari)
        chari_updated["house"] = None
        chari_updated["card_type"] = "38th Card"
        expected = (
            True,
            [chari_updated],
            []
        )
        actual = wiki_card_db.bifurcate_38s(
            [self.chari]
        )
        self.assertEqual(expected, actual)


    def test_process_skyjedi_card_batch(self):
        # From other tests above, get all the inputs and all
        # the expectations. Together run the whole shebang
        # here so the interactions between bifurcate functions
        # comes out correctly.
        # NOTE this test seems verbose and duplicative with the
        # tests above, but it keeps catching bugs where the
        # sequence of bifurcates has an issue. Worth it!

        ultra_mm_merged = copy.deepcopy(self.ultra1_mm)
        ultra_mm_merged["card_type"] = "Creature"
        ultra_momu_merged = copy.deepcopy(self.ultra2_momu)
        ultra_momu_merged["rarity"] = "Rare"

        johnny_toc_redem_updated = \
            copy.deepcopy(self.johnny_toc_redem)
        johnny_toc_redem_updated["card_title"] = \
            "Johnny Longfingers (Redemption)"

        chuff_mcw_updated = copy.deepcopy(self.chuff_mcw)
        chuff_mcw_updated["card_title"] = "Chuff Ape (Elders)"
        taengoo_mcw_updated = copy.deepcopy(self.taengoo_mcw)
        taengoo_mcw_updated["card_title"] = \
            "Agent Taengoo (Ironyx Rebels)"

        # Prophecies and Archon Powers just get some
        # schema manipulation.
        heads_updated = copy.deepcopy(self.heads)
        heads_updated["house"] = None
        heads_updated["card_type"] = "38th Card"
        chari_updated = copy.deepcopy(self.chari)
        chari_updated["house"] = None
        chari_updated["card_type"] = "38th Card"

        expected = [
            # Some single no-bifurcate cards.
            self.dew_cota, self.fear_cota,
            # Giants per-set merge.
            ultra_mm_merged, ultra_momu_merged,
            # Anomalies do not combine into one card.
            self.grim_anomaly, self.grim_gr,
            # Redemption variant becomes a new card.
            self.johnny_mm, johnny_toc_redem_updated,
            # Original card stays the same, while MCW
            # variants become a new card. A debut MCW
            # card also starts with the suffix.
            self.chuff_cota,
            chuff_mcw_updated, taengoo_mcw_updated,
            # Prophecies and Archon Powers just get some
            # schema manipulation.
            heads_updated, chari_updated,
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
                self.heads, self.chari,
            ]
        )

        # Ignores order of lists.
        self.assertCountEqual(expected, actual)


