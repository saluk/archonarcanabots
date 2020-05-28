try:
    import __updir__
except:
    pass
import passwords
import random
PASSWORD = passwords.MASTERVAULT_PASSWORD
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import exists
from sqlalchemy.dialects.postgresql import JSON, JSONB, insert
from sqlalchemy import Column, Integer, String, Table, ForeignKey, UniqueConstraint, ForeignKeyConstraint

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

def postgres_upsert(session, table, obs):
    for ob in obs:
        d = object_as_dict(ob)
        sql = insert(table, bind=session).values(d)
        sql = sql.on_conflict_do_update(
            index_elements = [c.key for c in inspect(table).primary_key],
            set_=d
        )
        session.execute(sql)

engine = sqlalchemy.create_engine('postgresql+psycopg2://mastervault:'+PASSWORD+'@localhost/mastervault',
    pool_size=20)
Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

class UpdateScope(object):
    def __init__(self):
        self.decks = []
        self.cards = []
    def add_deck(self, *args, **kwargs):
        deck = Deck(*args, **kwargs)
        self.decks.append(deck)
    def add_card(self, *args, **kwargs):
        card = Card(*args, **kwargs)
        self.cards.append(card)
    def commit(self):
        self.session = Session()
        postgres_upsert(self.session, Card, self.cards)
        postgres_upsert(self.session, Deck, self.decks)
        self.session.commit()
        self.cards = []
        self.decks = []
    def next_page_to_scrape(self, start_at):
        self.session = Session()
        pages = self.session.execute("""
        select page+1 from back_scrape_page scraped
        where NOT EXISTS (select null from back_scrape_page to_scrape 
                        where to_scrape.page = scraped.page +1) 
            and page>%d 
            order by page limit 1""" % start_at).first()
        self.session.close()
        if pages is None:
            return 1
        return int(pages[0])
    def scraped_page(self, *args, **kwargs):
        back_scrape_page = BackScrapePage(*args, **kwargs)
        self.session = Session()
        if self.session.query(BackScrapePage).filter(BackScrapePage.page==back_scrape_page.page).first():
            self.session.commit()
            return
        self.session.add(back_scrape_page)
        self.session.commit()
    def get_proxy(self):
        self.session = Session()
        proxy = self.session.query(GoodProxy).order_by(func.random()).limit(1).first()
        if not proxy:
            self.session.commit()
            return None
        ip_port = proxy.ip_port
        self.session.commit()
        return ip_port
    def add_proxy(self, ip_port):
        self.session = Session()
        existing = self.session.query(GoodProxy).filter(GoodProxy.ip_port==ip_port).first()
        if existing:
            self.session.commit()
            return
        proxy = GoodProxy(ip_port=ip_port)
        self.session.add(proxy)
        self.session.commit()
    def remove_proxy(self, ip_port):
        return
    def session_reset(self):
        if self.session:
            self.session.close()
    # 452, 453, 341, 479, 435
    def get_cards(self, expansion=479):
        self.session = Session()
        cards = self.session.query(Card).filter(
            Card.deck_expansion==expansion,
            Card.data['is_enhanced']=='false',
            Card.data['is_maverick']=='false').all()
        print(len(cards))
        card_names = {}
        for c in cards:
            print(c.key)
            if c.data["card_type"]=="Creature2":
                continue
            if c.name in card_names:
                if card_names[c.name].data['house'] != c.data['house']:
                    card_names[c.name].data['house'] += " • " + c.data['house']
                continue
            # TODO fix legacies
            # select * from decks where data->'_links'->'cards'@>'"a7621926-1f0f-4d56-b2aa-15efdded15a9"' and expansion=435;
            #select * from decks where data->'set_era_cards'->'Legacy'@>'"a7621926-1f0f-4d56-b2aa-15efdded15a9"' limit 1;
            #a_deck = self.session.execute(
            #    "select * from decks where data->'set_era_cards'->'Legacy'@>'\"%s\"' and expansion=%s limit 1" % (c.key, expansion)).first()
            #print(a_deck)
            #if(a_deck):
            #    continue
            if c.data['expansion'] != expansion:
                continue
            if c.name=='Troll':
                print(a_deck.data)
                return []
            card_names[c.name] = c
        print(sorted(card_names.keys()))
        return card_names.values()

class BackScrapePage(Base):
    __tablename__ = "back_scrape_page"
    page = Column(Integer, primary_key=True)
    decks_scraped = Column(Integer)
    cards_scraped = Column(Integer)

class GoodProxy(Base):
    __tablename__ = "good_proxies"
    inc = Column(Integer, primary_key=True, autoincrement=1, default=1)
    ip_port = Column(String, primary_key=True)

class Deck(Base):
    __tablename__ = 'decks'
    key = Column(String, primary_key=True, unique=True)
    name = Column(String)
    expansion = Column(Integer)
    data = Column(JSONB)
    cards = relationship('Card', secondary='deck_cards')

# TODO handle legacies
class Card(Base):
    __tablename__ = 'cards'
    key = Column(String, primary_key=True)
    deck_expansion = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(JSONB)
    UniqueConstraint('key', 'deck_expansion')

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

print("before create")
Base.metadata.create_all(engine)
print("after create")

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

if __name__=="__main__":
    scope = UpdateScope()
    #print(len(scope.get_cards()))
    #scope.add_proxy('http://205.126.14.171:800')
    #scope.add_proxy('http://104.154.143.77:3128')
    for i in "10000 13000 16000 23000 28000 31000 33000 35000 37000 42000 54000 62000 65000".split(" "):
        print(i, scope.next_page_to_scrape(int(i)))

"""
    scope = UpdateScope()
    scope.add_card(key='a', deck_expansion="341", name='my card', data={'key':'a','expansion':'341', 'extra':2})
    scope.add_card(key='b', deck_expansion="435", name='my card', data={'key':'b','expansion':'435'})
    scope.add_card(key='b', deck_expansion="341", name='my card', data={'key':'b','expansion':'435'})
    scope.add_deck(key='deck1', name='My First Deck X', expansion='341', data={'key':'deck1', 'name':'some name'})

    scope.commit()

    session = Session()
    card = session.query(Card).filter_by(key='a').first()
    print(object_as_dict(card))

    card = session.query(Deck).filter_by(key='deck1').first()
    print(object_as_dict(card))

    #for card in session.query(Card).all():
    #    session.delete(card)
    #session.commit()
"""