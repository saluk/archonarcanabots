import pytest
import sys, os
sys.path.insert(0, os.path.abspath(__file__).rsplit("/", 1)[0]+'/..')
from models import wiki_model

#print(modify_card_text("", ))
#print(modify_card_text("This creature gains, \"Reap: Play the top card of your deck.\"", 'Austeralis Seaborg'))

@pytest.mark.parametrize(
    "card_name, text, transform",
    [
        ("Mookling", 
            "Your opponent's keys [[Cost|cost]] +X\uf360, where X is Mookling's power.",
            "Your opponent's keys [[Cost|cost]] +X{{Aember}}, where X is Mookling's power."),
        ("Amberfin Shark",
            "'''Play:''' Give \u00c6mberfin Shark three +1 power counters. <p> At the end of your turn, remove a +1 power counter from \u00c6mberfin Shark. [[if you do|If you do]], each player gains 1\uf360.",
            "'''Play:''' Give \u00c6mberfin Shark three +1 power counters. <p> At the end of your turn, remove a +1 power counter from \u00c6mberfin Shark. [[if you do|If you do]], each player gains 1{{Aember}}."),
        ('Austeralis Seaborg',
            "\uf566 Reap: Deal 2\uf361 to a creature. If this damage destroys that creature, raise the [[Tide|tide]].",
            "{{Tide}} '''Reap:''' Deal 2{{Damage}} to a creature. If this damage destroys that creature, raise the [[Tide|tide]]."),
        ('Austeralis Seaborg',
            "This creature gains, \"Reap: Play the top card of your deck.\"",
            "This creature gains, \"'''Reap:''' Play the top card of your deck.\""),
    ]
)
def test_unicode_replace(card_name, text, transform):
    assert wiki_model.modify_card_text(text, card_name) == transform