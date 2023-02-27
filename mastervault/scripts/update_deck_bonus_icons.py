try:
    import __updir__
except Exception:
    pass
from models.mv_model import Session, Deck, CardEnhancementsOld
from sqlalchemy import update

f = open("data/updated_deck_bonus_ids")
deck_ids = f.read().split("\n")
f.close()

def update_deck_bonus(deck_id):
    session = Session()
    # Get all of the bonus icons in the deck from the CardEnhancementsOld table
    bonus_icons = []
    for match in session.query(CardEnhancementsOld).filter(CardEnhancementsOld.deck_id==deck_id):
        bonus_icons.append(
            {
                "card_id": str(match.card_id),
                "bonus_icons": match.bonus_icons
            }
        )
    print(bonus_icons)
    for deck in session.query(Deck).filter(Deck.key==deck_id):
        print(deck.data)
        data = deck.data.copy()
        data["bonus_icons"] = bonus_icons
        session.execute(update(Deck).where(Deck.key==deck_id).values(data=data))
        session.commit()
    session.close()

updated_count = 0
for deck_id in deck_ids:
    print(deck_id, updated_count)
    update_deck_bonus(deck_id)
    updated_count += 1

print(f"updated decks: {updated_count}")