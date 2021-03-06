import __updir__
from models import mv_model
from datetime import datetime, timedelta
import time
import logging

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
        self.count_decks_expansion(session)
        logging.debug("--getting distinct")
        for expansion in session.query(mv_model.Deck.expansion).distinct():
            self.count_decks_expansion(session, expansion)
        session.commit()
        logging.debug(">>decks counted")

    def count_decks_expansion(self, session, expansion=None):
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