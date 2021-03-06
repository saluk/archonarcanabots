from collections import defaultdict
from models.wiki_model import card_data
from sqlalchemy.engine.base import TwoPhaseTransaction
import __updir__
from models import mv_model, shared
from datetime import datetime, timedelta
import time
import logging
import re

logging.basicConfig(filename="/opt/archonarcanabots/cron.log", level=logging.DEBUG)

class Workers:
    def __init__(self):
        self.timers = [
            {
                "name": "count decks",
                "time": 60,
                "func": self.count_decks
            }
        ]
        self.timers = []
        for t in self.timers:
            t["next_time"] = time.time()
        self.realtime_scrape_upload_method = 'full'

    def thread(self):
        """For each job in timers, run them once at start, then wait for the timer to count up and reset"""
        while 1:
            for t in self.timers:
                if time.time() > t["next_time"]:
                    t["func"]()
                    t["next_time"] = time.time() + t["time"]
            time.sleep(30)

    def count_decks(self):
        logging.debug("counting decks")
        session = mv_model.Session()
        self._count_decks_expansion(session)
        logging.debug("--getting distinct")
        for expansion in session.query(mv_model.Deck.expansion).distinct():
            self._count_decks_expansion(session, expansion)
        session.commit()
        logging.debug(">>decks counted")

    def new_cards(self, cards, savedb=False):
        from models import wiki_card_db
        import util
        session = mv_model.Session()
        recognized_sets = list(shared.get_set_numbers())
        if not cards:
            cardq = session.query(mv_model.Card)
            #cardq = cardq.filter(mv_model.Card.deck_expansion.notin_([str(x) for x in recognized_sets]))
            # for testing
            cardq = cardq.filter(mv_model.Card.deck_expansion.in_(["341","452"]))
            cardq = cardq.order_by(mv_model.Card.name,mv_model.Card.key)
            cards = cardq.all()
        process_cards = defaultdict(lambda: [])
        print("Checking for new cards:")
        for card in cards:
            if not card.is_from_current_set:
                continue
            if card.is_maverick: continue
            if card.is_enhanced: continue
            process_cards[card.data["card_title"]].append(card.data)
        for card_name, card_datas in process_cards.items():
            new_card_data = card_datas[0]
            if len(card_datas) > 1:
                print("## Do something with card that can transform", card_name)
                types = set([card["card_type"] for card in card_datas])
                houses = set([card["house"] for card in card_datas])
                if len(types) > 1:
                    if not [x for x in types if x not in ["Creature1", "Creature2"]]:
                        new_card_data.update([card for card in card_datas if card["card_type"] == "Creature1"][0])
                        print(" - it's a giant")
                    else:
                        raise Exception(f"Unknown type mismatch {card_name} {types}")
                if new_card_data["is_anomaly"]:
                    print(" - it's an anomaly")
                    new_card_data["house"] = "Anomaly"
                elif len(houses) > 1:
                    new_card_data["house"] = util.SEPARATOR.join(houses)
                    print(" - it's multihouse", new_card_data["house"])
            new_card = wiki_card_db.add_card(new_card_data, wiki_card_db.cards)
            print(new_card["card_title"], new_card["house"])
            if len(wiki_card_db.cards[new_card["card_title"]].keys()) > 1:
                print("> updating old set:", new_card["card_title"], wiki_card_db.cards[new_card["card_title"]].keys())
                #tool_update_decks.upload_set(card.name)
            else:
                print("< create new data", new_card["card_title"])
                #tool_update_decks.upload(card.name)
                #if self.realtime_scrape_upload_method == "full":
                #    tool_update_decks.create_page_view(card.name)
            # TODO for testing
            #break
        if savedb:
            wiki_card_db.save_json()
        print("Done", len(process_cards))

    def _count_decks_expansion(self, session, expansion=None):
        logging.debug("--counting %s", expansion)
        expansion_label = ""
        if expansion:
            expansion_label = "_%s" % expansion
        deckq = session.query(mv_model.Deck)
        if expansion:
            deckq = deckq.filter(mv_model.Deck.expansion==expansion)
        total = deckq.count()
        logging.debug("--total: %s", total)
        
        month_time = datetime.now()
        deckq = session.query(mv_model.Deck)
        if expansion:
            deckq = deckq.filter(mv_model.Deck.expansion==expansion)
        deckq = deckq.filter(
            mv_model.Deck.scrape_date>month_time-timedelta(weeks=4),
            mv_model.Deck.scrape_date<month_time
        )
        month = deckq.count()
        logging.debug("--month: %s", month)

        deckq = session.query(mv_model.Deck)
        if expansion:
            deckq = deckq.filter(mv_model.Deck.expansion==expansion)
        deckq = deckq.filter(
            mv_model.Deck.scrape_date>month_time-timedelta(weeks=4*2),
            mv_model.Deck.scrape_date<month_time-timedelta(weeks=4)
        )
        month_prev = deckq.count()
        logging.debug("--month_prev: %s", month_prev)

        week_time = datetime.now()
        deckq = session.query(mv_model.Deck)
        if expansion:
            deckq = deckq.filter(mv_model.Deck.expansion==expansion)
        deckq = deckq.filter(
            mv_model.Deck.scrape_date>week_time-timedelta(weeks=1),
            mv_model.Deck.scrape_date<week_time
        )
        week = deckq.count()
        logging.debug("--week: %s", week)

        deckq = session.query(mv_model.Deck)
        if expansion:
            deckq = deckq.filter(mv_model.Deck.expansion==expansion)
        deckq = deckq.filter(
            mv_model.Deck.scrape_date>week_time-timedelta(weeks=2),
            mv_model.Deck.scrape_date<week_time-timedelta(weeks=1)
        )
        week_prev = deckq.count()
        logging.debug("--week_prev: %s", week_prev)

        total_count = mv_model.Counts(label="total_deck_count"+expansion_label, count=total)
        session.merge(total_count)
        month_count = mv_model.Counts(label="month_deck_count"+expansion_label, count=month)
        session.merge(month_count)
        week_count = mv_model.Counts(label="week_deck_count"+expansion_label, count=week)
        session.merge(week_count)
        prev_month_count = mv_model.Counts(label="prev_month_deck_count"+expansion_label, count=month_prev)
        session.merge(prev_month_count)
        prev_week_count = mv_model.Counts(label="prev_week_deck_count"+expansion_label, count=week_prev)
        session.merge(prev_week_count)
        logging.debug("--merged")

if __name__ == "__main__":
    w = Workers()
    w.count_decks()