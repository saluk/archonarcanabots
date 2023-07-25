try:
    import __updir__
except Exception:
    pass
import util
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import backref
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import text, func, update, bindparam
from sqlalchemy.sql import exists
from sqlalchemy.dialects.postgresql import JSONB, insert, ARRAY
from sqlalchemy import Column, Integer, Boolean, String, DateTime
from sqlalchemy import Table, ForeignKey, UniqueConstraint, ForeignKeyConstraint, Sequence
import datetime
from models import wiki_model, shared
import re
import time
import hashlib

try:
    import passwords
    PASSWORD = passwords.MASTERVAULT_PASSWORD
except:
    passwords = None
    PASSWORD = None


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs
            if c.key != "global_index"}  # TODO check for generated column not global index


def postgres_upsert(session, table, obs):
    for ob in obs:
        d = object_as_dict(ob)
        sql = insert(table).values(d)
        sql = sql.on_conflict_do_update(
            #constraint = inspect(table).primary_key,
            index_elements = [c.key for c in inspect(table).primary_key],
            set_=d
        )
        session.execute(sql)

if passwords:
    engine = sqlalchemy.create_engine(
        'postgresql+psycopg2://mastervault:'+PASSWORD+'@localhost/mastervault',
        pool_size=5,
        pool_pre_ping=True,
        pool_recycle=3600
        #echo=True,
        #executemany_mode='batch'
    )
    Session = scoped_session(sessionmaker(bind=engine))
    Base = declarative_base()
else:
    engine = None
    Session = None
    Base = declarative_base()


class UpdateScope(object):
    def begin(self):
        self.cards = []
        self.decks = []
        self.deck_cards = []

    def add_deck(self, *args, **kwargs):
        kwargs["scrape_date"] = datetime.datetime.now()
        deck = Deck(*args, **kwargs)
        self.decks.append(deck)
        card_keys = set([card_key for card_key in deck.data["_links"]["cards"]])
        for card_key in card_keys:
            self.deck_cards.append(DeckCard(
                deck_key=deck.key,
                card_key=card_key,
                card_deck_expansion=deck.expansion,
                count=deck.count(card_key)
            ))

    def add_card(self, *args, **kwargs):
        card = Card(*args, **kwargs)
        self.cards.append(card)

    def commit(self):
        # TODO bad circular import
        from models import deck_card_search
        print("BEFORE COMMIT")
        session = Session()
        #print([o.key for o in self.decks])
        #print([(o.key, o.deck_expansion) for o in self.cards])
        print( "sesion made")
        try:
            postgres_upsert(session, Deck, self.decks)
            print(" upserted decks")
            postgres_upsert(session, Card, self.cards)
            print(" upserted cards")
            postgres_upsert(session, DeckCard, self.deck_cards)
            print(" upserted deck_cards")
            for deck in self.decks:
                deck_card_search.create_deck_index(session, deck, True)
            session.commit()
            print(" commit made")
        except:
            import traceback
            traceback.print_exc()
            session.rollback()
            session.close()
            print(" session closed")
            raise

    def next_page_to_scrape(self, start_at):
        session = Session()
        possible = []
        if not session.query(BackScrapePage).filter(BackScrapePage.page == start_at).first():
            return start_at
        if not session.query(BackScrapePage).filter(BackScrapePage.page == start_at+1).first():
            return start_at+1
        pages = session.execute("""
        select page+1 from back_scrape_page scraped
        where NOT EXISTS (select null from back_scrape_page to_scrape
                        where to_scrape.page = scraped.page +1)
            and page>%s
            order by page limit 1""" % start_at).first()
        session.close()
        if pages:
            possible.append(int(pages[0]))
        if pages is None:
            if start_at == 1:
                return 1
            return start_at+1
        return min(possible)

    def next_scrape_task(self):
        session = Session()
        next = session.query(ScrapePageTask).filter(ScrapePageTask.rescrape_complete==False)\
            .order_by(ScrapePageTask.page.asc()).first()
        return next
    
    def scraped_page_task(self, task, decks_scraped, cards_scraped):
        session = Session()
        task = session.query(ScrapePageTask).filter(ScrapePageTask.page==task.page, ScrapePageTask.per_page==task.per_page).first()
        if not task:
            session.close()
            return
        task.decks_scraped = decks_scraped
        task.cards_scraped = cards_scraped
        if task.decks_scraped == task.per_page:
            task.rescrape_complete = True
        session.add(task)
        if task.scrape_next_page:
            next_task = ScrapePageTask(page=task.page+1, per_page=task.per_page, scrape_next_page=True)
            session.add(next_task)
        session.commit()
        session.close()

    def start_page(self, page):
        session = Session()
        found = session.query(BackScrapePage).filter(BackScrapePage.page==page).first()
        if found and found.scraping:
            print(" already scraping...")
            return None
        if not found:
            found = BackScrapePage(page=page, scraping=1)
        else:
            found.scraping = 1
        session.add(found)
        try:
            session.commit()
        except Exception:
            session.close()
            return False
        return True

    def scraped_page(self, page, decks_scraped, cards_scraped):
        session = Session()
        back_scrape_page = session.query(BackScrapePage).filter(BackScrapePage.page==page).first()
        if not back_scrape_page:
            session.close()
            return
        back_scrape_page.decks_scraped = decks_scraped
        back_scrape_page.cards_scraped = cards_scraped
        session.add(back_scrape_page)
        session.commit()
        session.close()

    def clean_scrape(self, page=None):
        session = Session()
        if page:
            session.execute(text("""
            delete from back_scrape_page
            where page=%d""" % page))
        else:
            session.execute(text("""
            delete from back_scrape_page
            where decks_scraped IS NULL OR decks_scraped<24"""))
        session.commit()
        if page:
            return
        pages = session.query(BackScrapePage).filter(BackScrapePage.scraping==1).all()
        for p in pages:
            p.scraping = None
            session.add(p)
        session.commit()

    def get_proxy(self):
        session = Session()
        proxy = session.query(GoodProxy).order_by(func.random()).limit(1).first()
        if not proxy:
            session.commit()
            return None
        ip_port = proxy.ip_port
        session.commit()
        return ip_port

    def add_proxy(self, ip_port):
        session = Session()
        existing = session.query(GoodProxy).filter(GoodProxy.ip_port==ip_port).first()
        if existing:
            session.commit()
            return
        proxy = GoodProxy(ip_port=ip_port)
        session.add(proxy)
        session.commit()

    def remove_proxy(self, ip_port):
        return
    # 452, 453, 341, 479, 435

    def get_cards(self, expansion=None):
        print("getting cards")
        session = Session()
        cards = session.query(Card).filter(
            Card.data['is_enhanced']=='false',
            Card.data['is_maverick']=='false')
        if expansion:
            cards = cards.filter(Card.data['expansion']==str(expansion))
        cards = cards.all()
        return cards

    def get_locale_cards(self, locale=None):
        print("getting locale")
        session = Session()
        cards = session.query(LocaleCard)
        cards = cards.all()
        print(len(cards))
        return cards

    # TODO move to migration module, add the index removal part
    def update_add_name_sane(self, batch_size=1000):
        # Remvove index decks_name_sane_trgrm
        session = Session()
        batch = 0
        while 1:
            start = time.time()
            print("batch:", batch)
            batch += 1
            next_batch = session.query(Deck).filter(
                Deck.name_sane == None
            ).limit(batch_size)
            decks = []
            print("query batch")
            for deck in next_batch.all():
                deck.sanitize_name()
                decks.append({
                    "key": deck.key,
                    "name_sane": deck.name_sane
                })
            if not decks:
                break
            print("bulk update")
            session.bulk_update_mappings(Deck, decks)
            print("commit")
            session.commit()
            print(" time:", time.time()-start)
        # TODO add this
        # Add index
        #session.execute(text('create index "decks_name_sane_trgrm" on decks using gin (name_sane gin_trgm_ops)'))



class BackScrapePage(Base):
    """Older model where we keep track of how many cards and decks are scraped on a given page"""
    __tablename__ = "back_scrape_page"
    page = Column(Integer, primary_key=True)
    decks_scraped = Column(Integer)
    cards_scraped = Column(Integer)
    scraping = Column(Integer)


class ScrapePageTask(Base):
    __tablename__ = "scrape_page_task"
    page = Column(Integer, primary_key=True)
    per_page = Column(Integer, primary_key=True, default=24)
    decks_scraped = Column(Integer)
    cards_scraped = Column(Integer)
    rescrape_complete = Column(Boolean, default=False)
    scrape_next_page = Column(Boolean, default=False)


class GoodProxy(Base):
    __tablename__ = "good_proxies"
    inc = Column(Integer, primary_key=True, autoincrement=1, default=1)
    ip_port = Column(String, primary_key=True)


class Deck(Base):
    __tablename__ = 'decks'
    key = Column(String, primary_key=True, unique=True)
    page = Column(Integer)   # MV page we scraped from
    index = Column(Integer)  # index on MV page we scraped from
    scrape_date = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String)
    name_sane = Column(String)
    expansion = Column(Integer)
    data = Column(JSONB)
    global_index = Column(Integer)  # Generated value based on page*24-24+1+index
    cards = relationship('Card', secondary='deck_cards')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.name:
            self.sanitize_name()

    def sanitize_name(self):
        self.name_sane = util.sanitize_deck_name(self.name)

    @property
    def houses(self):
        return sorted(self.data['_links']['houses'])

    def get_unique_card_keys(self):
        return set(self.data['_links']['cards'])

    def get_cards(self):
        """Returns all cards including duplicates, also tags is_legacy for legacy cards.
        If any of the cards are listed as having bonus icons, include them in the bonus_icons field"""
        for c in sorted(self.cards, key=lambda card: card.data['house']):
            for i in range(self.data['_links']['cards'].count(c.key)):
                c.data['is_legacy'] = c.key in self.data.get('set_era_cards',{}).get('Legacy',[])
                c.data['bonus_icons'] = []
                for bonus_card in self.data.get("bonus_icons", []):
                    if bonus_card["card_id"] == c.key:
                        c.data['bonus_icons'] = bonus_card['bonus_icons']
                yield c

    def get_locale_cards(self, session, locale):
        i = 0
        for card in self.get_cards():
            for locale_card in session.query(LocaleCard).filter(LocaleCard.en_name==card.name, LocaleCard.locale==locale, LocaleCard.key==card.key):
                i += 1
                if i>100:
                    break
                yield locale_card

    def get_legacy_card_ids(self):
        return self.data.get('set_era_cards',{}).get('Legacy',[])

    def count(self, card_key):
        return self.data["_links"]["cards"].count(card_key)

    def get_houses(self):
        return self.data['_links']['houses']


class CardEnhancementsOld(Base):
    __tablename__ = "card_enhancements_old"
    deck_id = Column(String, primary_key=True)
    card_id = Column(String, primary_key=True)
    bonus_icons = Column(ARRAY(String, dimensions=1))
    card_index = Column(Integer, primary_key=True)


class TwinDeck(Base):
    __tablename__ = "twin_decks"
    evil_key = Column(String, ForeignKey(Deck.key), primary_key=True)
    standard_key = Column(String, ForeignKey(Deck.key), unique=True)
    evil_deck = relationship('Deck', foreign_keys=[evil_key], backref=backref('evil', lazy='dynamic'))
    standard_deck = relationship('Deck', foreign_keys=[standard_key], backref=backref('standard', lazy='dynamic'))
        

# TODO handle indexes

# TODO handle legacies
# mavericks sometimes appear under a newer expansion than the card expansion:
#   we should set the card expansion according to its deck when it is a non-maverick
# legacy cards should be from an older expansion. we want to use the card expansion
#   as our expansion and NOT the deck expansion


class Card(Base):
    __tablename__ = 'cards'
    key = Column(String, primary_key=True)
    deck_expansion = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(JSONB)
    decks = relationship("Deck", secondary="deck_cards", lazy="dynamic", viewonly=True)
    UniqueConstraint('key', 'deck_expansion')
    
    @property
    def card_type(self):
        # From mastervault
        return self.data["card_type"]

    @property
    def is_anomaly(self):
        # This is stored in the mastervault already
        return self.data["is_anomaly"]

    @property
    def is_maverick(self):
        return self.data["is_maverick"]

    @property
    def is_from_current_set(self):
        return self.is_anomaly or self.deck_expansion == self.data['expansion']  #Anomalies get their own expansion so are technically always from their own set

    @property
    def is_enhanced(self):
        return self.data["is_enhanced"]

    def aa_format(self):
        return wiki_model.card_data({**self.data})

###
# Experiment on fast deck searching for card matches
class T_CARD_INDEX(Base):
    __tablename__ = "t_card_index"
    index = Column(String, primary_key=True)
    name = Column(String)

class T_DECK_CARDS(Base):
    __tablename__ = "t_deck_cards"
    deck_key = Column(String, primary_key=True)
    cards = Column(String)


class LocaleCard(Base):
    __tablename__ = 'locale_card'
    en_name = Column(String, ForeignKey("cards.name"), primary_key=True)
    key = Column(String, primary_key=True)
    locale = Column(String, primary_key=True)
    deck_expansion = Column(Integer)
    data = Column(JSONB)


class DeckCard(Base):
    __tablename__ = 'deck_cards'
    #id = Column(Integer, Sequence('deck_cards_id_seq'), unique=True)
    deck_key = Column(String, ForeignKey(Deck.key), primary_key=True)
    card_key = Column(String, primary_key=True)
    card_deck_expansion = Column(Integer, primary_key=True)
    count = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint(
            ['card_key', 'card_deck_expansion'],
            ['cards.key', 'cards.deck_expansion']
        ),
    )


class ApiUser(Base):
    __tablename__ = "api_user"
    uuid = Column(String, primary_key=True, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    dok_key = Column(String)
    keyforgegame_auth = Column(String)
    keyforgegame_uuid = Column(String)


class OwnedDeck(Base):
    __tablename__ = "deck_user"
    deck_key = Column(String, ForeignKey(Deck.key), primary_key=True)
    user_key = Column(String, ForeignKey(ApiUser.uuid), primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)


class Counts(Base):
    __tablename__ = "counts"
    label = Column(String, primary_key=True)
    count = Column(Integer)
    meta = Column(JSONB)


class CardCounts(Base):
    __tablename__ = "card_counts"
    name = Column(String, primary_key=True)
    deck_expansion = Column(Integer, primary_key=True)
    data = Column(JSONB)


class HouseCounts(Base):
    __tablename__ = 'house_counts'
    name = Column(String, primary_key=True)
    deck_expansion = Column(Integer, primary_key=True)
    count = Column(Integer)


class DeckStatCounted(Base):
    """ This is just a record of the most recent deck that we have added into our stats """
    __tablename__ = "deck_stat_counted"
    label = Column(String, primary_key=True)
    start = Column(Integer) # deck.page * 24 + deck.index

if Session:
    print("before create")
    Base.metadata.create_all(engine)
    print("after create")

# TODO move to a migration module
def add_deck_cards():
    session = Session()
    amt = 0
    while 1:
        decks = session.query(Deck).filter(
            ~exists().where(DeckCard.deck_key==Deck.key)
        ).limit(1000).all()
        if not decks:
            break
        for deck in decks:
            added = {}
            for card_key in deck.data["_links"]["cards"]:
                if card_key not in added:
                    new_card = DeckCard(deck_key=deck.key, card_key=card_key, card_deck_expansion=deck.expansion, count=1)
                    session.add(new_card)
                    added[card_key] = new_card
                else:
                    added[card_key].count += 1
            session.commit()
            amt += 1
            print(deck.key, amt)


if Session:
    # Every time we start up, clean up from before
    UpdateScope().clean_scrape()


if __name__ == "__main__":
    scope = UpdateScope()
    session = Session()
    q = session.query(Deck)
    decks = q.filter(Deck.global_index==3000000).all()
    print(decks[0].name)
    #scope.add_proxy('http://205.126.14.171:800')
    #scope.add_proxy('http://104.154.143.77:3128')
    holes = []
    i = 1
    while 1:
        break
        next = scope.next_page_to_scrape(int(i))
        print(i,next)
        if i==next:
            i = next+1
        else:
            i = next
        if i>76000:# or i == 1:
            break
