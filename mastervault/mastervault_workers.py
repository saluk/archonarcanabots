import sys
from collections import defaultdict
from sqlalchemy.engine.base import TwoPhaseTransaction
from sqlalchemy import or_
from sqlalchemy.sql.functions import concat
import __updir__
from models import mv_model, shared, wiki_card_db
from datetime import datetime, timedelta
import time
import logging
import re
from twilio.rest import Client

logging.basicConfig(
    filename="/opt/archonarcanabots/cron.log",
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger().addHandler(logging.StreamHandler())

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
        from mastervault.mastervault import MasterVault
        self.mv = MasterVault()

    def text_alert(self, msg):
        import passwords
        client = Client(passwords.TWILIO_ACCOUNT_SID, passwords.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=msg,
            from_='(469) 405-3249',
            to='12063835762'
        )
        logging.debug("twilio.send %s", msg)

    def discord_alert(self, msg):
        import passwords
        import requests
        r = requests.post(passwords.DISCORD_WEBHOOK, json={"content": msg})

    def alert(self, msg, methods=[]):
        if 'text' in methods:
            self.text_alert(msg)
        if 'discord' in methods:
            self.discord_alert(msg)

    def deck_scrape_lag(self):
        from mastervault import mastervault
        session = mv_model.Session()
        deckq = session.query(mv_model.Deck)
        total_scraped = deckq.count()
        total_official = mastervault.get_mastervault_deck_count()
        lag = total_official-total_scraped + 1
        print(f"{total_official} {total_scraped} {lag}")
        if lag > 25:
            self.discord_alert(f"(Test) Deck scrape is {lag} decks behind. Official count: {total_official} Scrape count: {total_scraped}")

    def count_decks(self):
        logging.debug("counting decks")
        session = mv_model.Session()
        self._count_decks_expansion(session)
        logging.debug("--getting distinct")
        for expansion in session.query(mv_model.Deck.expansion).distinct():
            self._count_decks_expansion(session, expansion)
        session.commit()
        logging.debug(">>decks counted")

    def new_cards(self, cards=None, savedb=True, only_new_edits=False):
        # TODO refactor this method into a class/module
        import util
        import tool_update_cards
        import connections
        scope = mv_model.UpdateScope()
        session = mv_model.Session()
        recognized_sets = list(shared.get_set_numbers())
        if not cards:
            cardq = session.query(mv_model.Card)
            cardq = cardq.filter(or_(
                mv_model.Card.deck_expansion.notin_([str(x) for x in recognized_sets]),
                mv_model.Card.deck_expansion.in_([str(x) for x in shared.NEW_SETS])
            ))
            cardq = cardq.order_by(mv_model.Card.name,mv_model.Card.key)
            cards = cardq.all()
        logging.debug("\nChecking for new cards:\n")
        card_batch = [card for card in cards if (
            card.is_from_current_set and
            not card.is_maverick and
            not card.is_enhanced
        )]
        logging.debug([card.name for card in card_batch])
        card_datas = wiki_card_db.process_mv_card_batch(card_batch)
        wp = connections.get_wiki()
        processed_cards = {}
        changes = []
        for new_card_data in card_datas:
            new_card = wiki_card_db.add_card(new_card_data, wiki_card_db.cards)
            card = processed_cards[new_card["card_title"]] = wiki_card_db.cards[new_card["card_title"]]
            logging.debug("%s - %s", new_card["card_title"], new_card["house"])
            if [new_set for new_set in card if new_set not in recognized_sets] and len(card)>1:
                print("old set")
                logging.debug("> updating old set: %s, %s", new_card["card_title"], card.keys())
                if tool_update_cards.update_card_page_cargo(
                    wp, card, "updating reprint with new sets", "carddb", only_sets=True, 
                    pause=False
                ):
                    changes.append(("reprint", new_card["card_title"]))
                    self.alert("Worker updated reprint %s" % new_card["card_title"], ['discord'])
            else:
                print("new set")
                logging.debug("< create new data %s", new_card["card_title"])
                # Look for locale
                self._update_locales(new_card["card_title"])
                wiki_card_db.build_localization(
                    scope, 
                    wiki_card_db.cards, 
                    wiki_card_db.locales, 
                    from_cards=session.query(mv_model.LocaleCard).filter(mv_model.LocaleCard.en_name==new_card["card_title"]).all()
                )
                any_changes = 0
                if tool_update_cards.update_card_page_cargo(wp, card, "updating new card", "carddb", pause=False, only_new_edits=only_new_edits):
                    any_changes += 1
                # TODO CardLocaleData is all on one page, its inefficient to try and edit the page 11 times
                for locale in wiki_card_db.locale_db:
                    if locale=="en": continue
                    if new_card["card_title"] in wiki_card_db.locales[locale]:
                        locale_card = wiki_card_db.locales[locale][new_card["card_title"]]
                        card = wiki_card_db.cards[new_card["card_title"]]
                        if tool_update_cards.upload_image_for_card(wp, locale, locale_card):
                            any_changes += 1
                        if tool_update_cards.update_card_page_cargo(wp, card, "updating new card", "carddb", 
                            pause=False, locale=locale, only_new_edits=only_new_edits
                        ):
                            any_changes += 1
                #if tool_update_cards.update_cards_v2(
                #    wp, 
                #    card_name=new_card["card_title"], 
                #    update_reason="add card view for new card", 
                #    data_to_update="update_card_views",
                #    upload_image=True,
                #    pause=False,
                #    only_new_edits=only_new_edits
                #):
                #    any_changes += 1
                if any_changes:
                    changes.append(("new", new_card["card_title"]))
                    self.alert("Worker updated new card %s" % new_card["card_title"], ['discord'])
        if savedb:
            print("Saving json")
            wiki_card_db.build_links(processed_cards)
            #wiki_card_db.add_artists_from_text(wiki_card_db.cards)
            wiki_card_db.clean_fields(wiki_card_db.cards, {})
            wiki_card_db.save_json(wiki_card_db.cards, wiki_card_db.locales)
        logging.debug("Done: %s", len(card_datas))

    def _update_locales(self, card_title):
        for locale in wiki_card_db.locale_db:
            print(f"updating locale {locale} for {card_title}")
            try:
                locale_card = wiki_card_db.get_latest(card_title, locale=locale)
                print(f"  got card")
            except:
                print(f"  scraping locale")
                self.mv.scrape_cards_locale(locale, card_title=card_title, rescrape=False)

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

        total_count = mv_model.Counts(label="total_deck_count"+expansion_label, count=total, meta=datetime.now().ctime())
        session.merge(total_count)
        month_count = mv_model.Counts(label="month_deck_count"+expansion_label, count=month, meta=datetime.now().ctime())
        session.merge(month_count)
        week_count = mv_model.Counts(label="week_deck_count"+expansion_label, count=week, meta=datetime.now().ctime())
        session.merge(week_count)
        prev_month_count = mv_model.Counts(label="prev_month_deck_count"+expansion_label, count=month_prev, meta=datetime.now().ctime())
        session.merge(prev_month_count)
        prev_week_count = mv_model.Counts(label="prev_week_deck_count"+expansion_label, count=week_prev, meta=datetime.now().ctime())
        session.merge(prev_week_count)
        logging.debug("--merged")

    def update_card_stats(self):
        from models import card_stats
        card_stats.count_decks('card_counts', card_stats.do_card_counts, card_stats.commit_card_counts, 2)
        card_stats.count_decks('house_counts', card_stats.do_house_counts, card_stats.commit_house_counts, 2)
        card_stats.count_decks('evil_twins', card_stats.do_evil_twin, card_stats.commit_evil_twin, 2)

    def find_nice_twins(self):
        session = mv_model.Session()
        open_twins = list(session.query(mv_model.TwinDeck).filter(mv_model.TwinDeck.standard_key==None))
        print(f"Analyzing {len(open_twins)} twin decks")
        for potential_twin in open_twins:
            potential_twin_deck = potential_twin.evil_deck
            house_decks = session.query(mv_model.Deck).filter(mv_model.Deck.expansion==496)
            house_decks = house_decks.filter(
                concat(potential_twin_deck.name).like(
                    concat('%', mv_model.Deck.name, '%')
                )
            )
            for d in house_decks:
                if d.name == potential_twin_deck.name: continue
                print("found!", potential_twin_deck.name, '-', d.name)
                pt_card_names = sorted([c.name for c in potential_twin_deck.cards])
                t_card_names = sorted([c.name for c in d.cards])
                if pt_card_names == t_card_names:
                    print(" - matching cards")
                    potential_twin.standard_key = d.key
                    session.add(potential_twin)
                    session.commit()
                    self.alert(f'Found twin: {potential_twin.standard_key}, {potential_twin.evil_key}', ['discord'])
                    break

if __name__ == "__main__":
    w = Workers()
    getattr(w,sys.argv[1])(*sys.argv[2:])