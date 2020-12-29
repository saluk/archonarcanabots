from mastervault import datamodel
from datetime import datetime, timedelta
import time

class Workers:
    def __init__(self):
        self.timers = [
            {
                "name": "count decks",
                "time": 60,
                "func": self.count_decks
            }
        ]
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
        print("counting decks")
        session = datamodel.Session()
        self.count_decks_expansion(session)
        for expansion in session.query(datamodel.Deck.expansion).distinct():
            self.count_decks_expansion(session, expansion)
        session.commit()
        print(">>decks counted")

    def count_decks_expansion(self, session, expansion=None):
        expansion_label = ""
        if expansion:
            expansion_label = "_%s" % expansion
        deckq = session.query(datamodel.Deck)
        if expansion:
            deckq = deckq.filter(datamodel.Deck.expansion==expansion)
        total = deckq.count()
        
        month_time = datetime.now()
        deckq = session.query(datamodel.Deck)
        if expansion:
            deckq = deckq.filter(datamodel.Deck.expansion==expansion)
        deckq = deckq.filter(
            datamodel.Deck.scrape_date>month_time-timedelta(weeks=4),
            datamodel.Deck.scrape_date<month_time
        )
        month = deckq.count()

        deckq = session.query(datamodel.Deck)
        if expansion:
            deckq = deckq.filter(datamodel.Deck.expansion==expansion)
        deckq = deckq.filter(
            datamodel.Deck.scrape_date>month_time-timedelta(weeks=4*2),
            datamodel.Deck.scrape_date<month_time-timedelta(weeks=4)
        )
        month_prev = deckq.count()

        week_time = datetime.now()
        deckq = session.query(datamodel.Deck)
        if expansion:
            deckq = deckq.filter(datamodel.Deck.expansion==expansion)
        deckq = deckq.filter(
            datamodel.Deck.scrape_date>week_time-timedelta(weeks=1),
            datamodel.Deck.scrape_date<week_time
        )
        week = deckq.count()

        deckq = session.query(datamodel.Deck)
        if expansion:
            deckq = deckq.filter(datamodel.Deck.expansion==expansion)
        deckq = deckq.filter(
            datamodel.Deck.scrape_date>week_time-timedelta(weeks=2),
            datamodel.Deck.scrape_date<week_time-timedelta(weeks=1)
        )
        week_prev = deckq.count()

        total_count = datamodel.Counts(label="total_deck_count"+expansion_label, count=total)
        session.merge(total_count)
        month_count = datamodel.Counts(label="month_deck_count"+expansion_label, count=month)
        session.merge(month_count)
        week_count = datamodel.Counts(label="week_deck_count"+expansion_label, count=week)
        session.merge(week_count)
        prev_month_count = datamodel.Counts(label="prev_month_deck_count"+expansion_label, count=month_prev)
        session.merge(prev_month_count)
        prev_week_count = datamodel.Counts(label="prev_week_deck_count"+expansion_label, count=week_prev)
        session.merge(prev_week_count)