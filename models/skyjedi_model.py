import json5
import sys

class LocalJson(object):
    def __init__(self):
        self.cards = []

    def add_file(self, json_file):
        with open(json_file, "r") as f:
            cards = json5.load(f)
            self.cards.extend(cards)
            
    def get_cards(self):
        return self.cards
