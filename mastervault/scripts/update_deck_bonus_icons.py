import sys, os
sys.path.insert(0, os.path.abspath(__file__).rsplit("/", 1)[0]+'/../..')
from models.mv_model import Session, Deck, CardEnhancementsOld
from sqlalchemy import update

f = open("data/enhance_update.csv")
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

start_at = ""
updated_count = 0
for deck_id in deck_ids:
    if not deck_id.strip():
        continue
    print(deck_id, updated_count)
    updated_count += 1
    if start_at and start_at != deck_id:
        continue
    start_at = ""
    update_deck_bonus(deck_id)

print(f"updated decks: {updated_count}")