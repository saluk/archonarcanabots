import json5
import sys
from models import fancy_quotes
from models import modify_house


class LocalJson(object):
    def __init__(self):
        self.cards = []

    def add_file(self, json_file):
        print(".", end="")
        sys.stdout.flush()
        with open(json_file, "r") as f:
            cards = json5.load(f)

            for c in cards:
                c["card_title"] = fancy_quotes.force(
                    c["card_title"]
                )
                if "card_text" in c:
                    c["card_text"] = fancy_quotes.force(
                        c["card_text"]
                    )
                if "flavor_text" in c:
                    c["flavor_text"] = fancy_quotes.force(
                        c["flavor_text"]
                    )

                c["house"] = modify_house.as_needed(c)

            self.cards.extend(cards)

    def get_cards(self):
        print("done")
        sys.stdout.flush()
        return self.cards
