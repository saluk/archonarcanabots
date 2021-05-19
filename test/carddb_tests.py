from models.wiki_model import linking_keywords, sanitize_text
from models.wiki_card_db import linking_keywords, link_card_titles, all_traits, get_cargo, cards

print(get_cargo(cards["Ancient Bear"]))

t1 = "Elusive. (The first time this creature is attacked each turn, no damage is dealt.) <p> After a creature reaps, stun it."
t2 = "[[Elusive|Elusive]]. (The first time this creature is attacked each turn, no damage is dealt.) <p> After a creature reaps, stun it."
t3 = "[[Elusive|Elusive]]. (The first time this creature is attacked each turn, no damage is dealt.) <p> After a creature reaps, [[Stun|stun]] it."
assert linking_keywords(t1) == t3, linking_keywords(t1)
assert linking_keywords(t2) == t3, linking_keywords(t2)
assert linking_keywords(t3) == t3, linking_keywords(t3)
t4 = "[[Skirmish]]. (When you use this creature to fight, it is dealt no damage in [[return]].) <p> Fight: Draw a card. "
t5 = "[[Skirmish]]. (When you use this creature to fight, it is dealt no damage in return.) <p> Fight: Draw a card. "
assert (linking_keywords(t4)) == t5, linking_keywords(t4)
t6 = "'''Play:''' [[Return|Return]] an enemy creature to its owner’s hand."
t7 = "'''Play:''' Return an enemy creature to its owner’s hand."
assert (linking_keywords(t6)) == t7, linking_keywords(t6)
t8 = "'''Action:''' Purge a creature in play. If you do, your opponent gains control of Spangler Box. If Spangler Box leaves play, return to play all cards purged by Spangler Box."
t9 = "'''Action:''' [[Purge|Purge]] a creature in play. [[if you do|If you do]], your opponent gains [[Control|control]] of Spangler Box. If Spangler Box leaves play, return to play all cards [[Purge|purged]] by Spangler Box."
assert (linking_keywords(t8)) == t9, linking_keywords(t8)
t10 = "During your turn, if Captain Val Jericho is in the center of your battleline, you may play one card that is not of the active house."
t11 = "During your turn, if Captain Val Jericho is in the [[Center of the Battleline|center of your battleline]], you may play one card that is not of the active house."
assert (linking_keywords(t10)) == t11, linking_keywords(t10)
t12 = "After an enemy creature is destroyed while fighting, put a glory counter on The Colosseum. <p> '''Omni:''' If there are 6 or more glory counters on The Colosseum, remove 6 and forge a key at current cost."
t13 = "After an enemy creature is destroyed while fighting, put a glory counter on The Colosseum. <p> '''Omni:''' If there are 6 or more glory counters on The Colosseum, remove 6 and [[Timing_Chart#Forge_a_Key|forge a key]] at [[Cost|current cost]]."
assert (linking_keywords(t12)) == t13, linking_keywords(t12)
t14 = "'''Play:''' Discard the top card of your opponent’s deck and reveal their hand. You gain 1{{Aember}} for each card of the discarded card’s house revealed this way. Your opponent [[Repeat|repeat]]s the preceding effect on you."
t15 = "'''Play:''' Discard the top card of your opponent’s deck and reveal their hand. You gain 1{{Aember}} [[For each|for each]] card of the discarded card’s house revealed this way. Your opponent [[Repeat|repeat]]s the [[Preceding|preceding effect]] on you."
assert (linking_keywords(t14)) == t15, linking_keywords(t14)
t16 = "'''Play:''' Choose a creature. Deal 1{{Damage}} to it for each friendly creature. You may exalt a friendly creature to repeat the preceding effect."
t17 = "'''Play:''' Choose a creature. Deal 1{{Damage}} to it [[For each|for each]] friendly creature. You may [[Exalt|exalt]] a friendly creature to [[Preceding|repeat the preceding effect]]."
assert (linking_keywords(t16)) == t17, linking_keywords(t16)

assert sanitize_text("blah.") == "blah.", sanitize_text("blah.")
assert sanitize_text("blah..") == "blah.", repr(sanitize_text("blah.."))
assert sanitize_text("blah") == "blah"
assert sanitize_text("blah... something") == "blah... something"
assert sanitize_text("blah...") == "blah...", sanitize_text("blah...")
assert sanitize_text("'''Play:''' Deal 4{{Damage}} to a creature that is not on a [[Flank|flank]], with 2{{Damage}} [[Splash|splash]].\ufeff\ufeff") == "'''Play:''' Deal 4{{Damage}} to a creature that is not on a [[Flank|flank]], with 2{{Damage}} [[Splash|splash]]."
assert sanitize_text("\u201cThe Red Shroud will defend the Crucible\r\nfrom the threat of dark \u00e6mber.\u201d", flavor=True) == "\u201cThe Red Shroud will defend the Crucible from the threat of dark \u00e6mber.\u201d", repr(sanitize_text("\u201cThe Red Shroud will defend the Crucible\r\nfrom the threat of dark \u00e6mber.\u201d", flavor=True))
assert sanitize_text("something    \n    something else", flavor=True)=="something something else"


print(link_card_titles("something Orb of Wonder", "Lesser Oxtet"))
print(link_card_titles("something Orb of Wonder and Lesser Oxtet.", "Lesser Oxtet"))
print(link_card_titles("controller", "something"))
print(link_card_titles("So, this nonlethal [[containment field]]; how lethal do you want it?", "Containment Field"))
print(link_card_titles("“When you have eliminated the imp-ossible, whatever remains, however imp-robable, must be the truth.” – Quixo the ”Adventurer”", "Not Quixo"))
print(link_card_titles("'''Action:''' Fully [[Heal|heal]] an Ancient Bear. If there are no Ancient Bears in play, [[Search|search]] your deck and discard pile and put each Ancient Bear from them into your hand. [[if you do|If you do]], shuffle your discard pile into your deck.", "Not Quixo"))
print(repr(all_traits()))
