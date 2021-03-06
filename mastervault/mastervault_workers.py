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

    def new_cards(self):
        session = mv_model.Session()
        recognized_sets = list(shared.get_set_numbers())
        recognized_sets.remove(479)
        cardq = session.query(mv_model.Card)
        cardq = cardq.filter(mv_model.Card.deck_expansion.notin_([str(x) for x in recognized_sets]))
        cardq = cardq.order_by(mv_model.Card.name,mv_model.Card.key)
        checked_names = {}
        duplicated_names = {}
        print("Checking for new cards:")
        for card in cardq.all():
            if not card.is_from_current_set:
                continue
            if card.is_anomaly: continue  # TODO Not sure what to do about anomalies
            if card.is_maverick: continue
            if card.is_enhanced: continue
            if card.name in checked_names:
                duplicated_names[card.name] = 1
                continue
            checked_names[card.name] = 1
            print("doing something with card")
            print(card.name, card.deck_expansion, card.data)
            if card.is_eviltwin:
                print("upload the evil twin")
            else:
                print("upload the non evil twin")
        print("Done", len(checked_names))
        print("Duplicated", duplicated_names)
        """
        for each card in database cards that are new (aything with unrecognized deck_expansion?):
            check for mavericks, legacy, anomaly, is-enhanced
            search for evil twin data
            do we have this card already in a previous set:
                is this a non-legacy
                update setdata only
            if we have a non-maverick, non-legacy, non-anomaly, non-evil twin, non-enhanced:
                create/update CardData (hide them from searches though)
                upload translation too?
                include can-maverick, can-twin
            if we have an evil twin non-maverick, non-legacy, non-anomaly:
                create/update CardData for twin
            check for versions of that card in the database
            if we have *enough* decks we can probably mark this card as not new
        """

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
    w.new_cards()