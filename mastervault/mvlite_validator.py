# Load a final card JSON file and compare
# to a SkyJedi JSON file.
#
# python - mastervault.mvlite_validator --f1=JSON1 --f2=JSON2
#
#
#
# For Tokens of Change (855) the only diffs were:
#
#   - Scraped cards also have the localized title, like so:
#        "card_title": "Codex of True Names",
#        "card_title_en": "Codex of True Names",
#     This doesn't hurt anything.
#
#   - Four instances of apostrophe mismatch:
# 'values_changed': {
# "root[229]['card_title']": {'new_value': "Aero O'Fore",
#                             'old_value': 'Aero O’Fore'},
# "root[269]['card_title']": {'new_value': "Flint's Legend",
#                             'old_value': 'Flint’s Legend'},
# "root[270]['card_title']": {'new_value': "Flint's Map",
#                             'old_value': 'Flint’s Map'},
# "root[271]['card_title']": {'new_value': "Flint's Stash",
#                             'old_value': 'Flint’s Stash'}}}
#  This also looks fine.
#
#
#
# For Aember Skies (800) it took a lot more decks to find all
# the sky beasts, but in any case, the diffs were:
#
#  - Same thing with localized title, doesn't hurt anything.
##
#  - Five instances of apostrophe mismatch
#      same as above plus 'Minerva’s Wings'
#
#  - All of the sky beasts have this difference:
#      "house_variant": 4,  (MV lite)
#      "house_variant": "4" (SkyJedi from ~1 year ago)
#    Seems fine because this field is not mentioned in code.
#
#  - Sky beasts also don't match in card ID and often not
#       the house attribute, which is expected.


import argparse
import json5
from pprint import pprint
from deepdiff import DeepDiff

parser = argparse.ArgumentParser()
parser.add_argument('--f1', required=True, type=str)
parser.add_argument('--f2', required=True, type=str)


if __name__ == "__main__":
    args = parser.parse_args()

    jsona = None
    jsonb = None

    with open(args.f1, 'r') as f:
        jsona = json5.load(f)
    with open(args.f2, 'r') as f:
        jsonb = json5.load(f)

    jsona.sort(key=lambda c: c['card_number'])
    jsonb.sort(key=lambda c: c['card_number'])

    pprint(DeepDiff(jsona, jsonb))
