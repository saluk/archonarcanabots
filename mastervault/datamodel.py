try:
    import __updir__
except Exception:
    pass
import passwords
import util
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import text, func, update, bindparam
from sqlalchemy.sql import exists
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Table, ForeignKey, UniqueConstraint, ForeignKeyConstraint, Sequence
import datetime
import carddb
import re
import time

PASSWORD = passwords.MASTERVAULT_PASSWORD


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def postgres_upsert(session, table, obs):
    for ob in obs:
        d = object_as_dict(ob)
        sql = insert(table, bind=session).values(d)
        sql = sql.on_conflict_do_update(
            #constraint = inspect(table).primary_key,
            index_elements = [c.key for c in inspect(table).primary_key],
            set_=d
        )
        session.execute(sql)


engine = sqlalchemy.create_engine(
    'postgresql+psycopg2://mastervault:'+PASSWORD+'@localhost/mastervault',
    pool_size=20,
    #echo=True,
    #executemany_mode='batch'
)
Session = scoped_session(sessionmaker(bind=engine))

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
        for card_key in deck.data["_links"]["cards"]:
            self.deck_cards.append(DeckCard(deck_key=deck.key, card_key=card_key, card_deck_expansion=deck.expansion))

    def add_card(self, *args, **kwargs):
        card = Card(*args, **kwargs)
        self.cards.append(card)

    def commit(self):
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
            session.execute("""
            delete from back_scrape_page
            where page=%d""" % page)
        else:
            session.execute("""
            delete from back_scrape_page
            where decks_scraped IS NULL OR decks_scraped<24""")
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
        session = Session()
        cards = session.query(Card).filter(
            Card.data['is_enhanced']=='false',
            Card.data['is_maverick']=='false')
        if expansion:
            cards = cards.filter(Card.data['expansion']==str(expansion))
        cards = cards.all()
        # print(len(cards))
        card_names = {}
        for c in cards:
            #print(c.key)
            if c.data["card_type"]=="Creature2":
                continue
            if c.name in card_names:
                if card_names[c.name].data['house'] != c.data['house']:
                    card_names[c.name].data['house'] += util.SEPARATOR + c.data['house']
                continue
            if c.data['expansion'] != expansion:
                continue
            card_names[c.name] = c
        # print(sorted(card_names.keys()))
        return card_names.values()

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
    __tablename__ = "back_scrape_page"
    page = Column(Integer, primary_key=True)
    decks_scraped = Column(Integer)
    cards_scraped = Column(Integer)
    scraping = Column(Integer)


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

    def get_cards(self):
        """Returns all cards including duplicates"""
        for c in sorted(self.cards, key=lambda card: card.data['house']):
            for i in range(self.data['_links']['cards'].count(c.key)):
                yield c

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
    UniqueConstraint('key', 'deck_expansion')
    
    @property
    def card_type(self):
        return self.data["card_type"]

    def aa_format(self):
        return carddb.add_card({**self.data})


class DeckCard(Base):
    __tablename__ = 'deck_cards'
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


class OwnedDeck(Base):
    __tablename__ = "deck_user"
    deck_key = Column(String, ForeignKey(Deck.key), primary_key=True)
    user_key = Column(String, ForeignKey(ApiUser.uuid), primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)


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


# Every time we start up, clean up from before
UpdateScope().clean_scrape()
# 341, 435, 452, 453, 479
#for card_set in [341, 435, 452, 453, 479]:
#    print(card_set, len(UpdateScope().get_cards(card_set)))


if __name__ == "__main__":
    scope = UpdateScope()
    #print(len(scope.get_cards()))
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
