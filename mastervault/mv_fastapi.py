from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
import uuid
import time
import re
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt,JWTError
from datetime import datetime, timedelta
import sys, os, traceback
import base64
from models import mv_model
from sqlalchemy import or_, and_
import util
import passwords
import connections
from mastervault import dok, deck_writer
from passlib.context import CryptContext
from pydantic import BaseModel

#Use different connection options for server
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
engine = sqlalchemy.create_engine(
    'postgresql+psycopg2://mastervault:'+passwords.MASTERVAULT_PASSWORD+'@localhost/mastervault',
    pool_size=5,
    connect_args={'connect_timeout': 15}
)
Session = scoped_session(sessionmaker(bind=engine))

SECRET_KEY = "f16861df9f66125336d2f588c080b67f22a0c39267dd5127654b6bc71d9c1bbd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

mvapi = FastAPI(
    title = "Wormhole Vault Api",
    description = "A synced clone of keyforgegame.com mastervault and utility functions for Archon Arcana",
    version="1.0"
)
origins = ["https://archonarcana.com"]
mvapi.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
sentry_sdk.init(
    "https://9f4401b9166a405199414dfb625af120@o465720.ingest.sentry.io/5478890",
    traces_sample_rate=0.01
)
mvapi.add_middleware(SentryAsgiMiddleware)

class UserInDB(BaseModel):
    uuid: uuid.UUID
    email: str
    hashed_password: str
    dok_key: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email:str):
    session = Session()
    api_user = session.query(mv_model.ApiUser).filter(mv_model.ApiUser.email==email).first()
    session.close()
    if api_user:
        return UserInDB(uuid=api_user.uuid, email=api_user.email, 
                        hashed_password=api_user.hashed_password, dok_key=api_user.dok_key or '')
    return UserInDB(uuid=uuid.uuid4(), email="user_not_found", hashed_password=email, dok_key="")

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email:str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        print("JWTError")
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        print("No user")
        raise credentials_exception
    return user

@mvapi.post('/token', tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password",
                            headers={"WWW-Authenticate":"Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub":user.email}, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@mvapi.get('/user/decks', tags=["user-action"])
async def mydecks(current_user: UserInDB = Depends(get_current_user)):
    decks = []
    session = Session()
    print(str(session.query(mv_model.Deck).\
            join(mv_model.OwnedDeck, mv_model.OwnedDeck.deck_key==mv_model.Deck.key).\
            filter(mv_model.OwnedDeck.user_key==str(current_user.uuid)).\
            order_by(mv_model.Deck.page, mv_model.Deck.index)))
    for deck in session.query(mv_model.Deck).\
            join(mv_model.OwnedDeck, mv_model.OwnedDeck.deck_key==mv_model.Deck.key).\
            filter(mv_model.OwnedDeck.user_key==str(current_user.uuid)).\
            order_by(mv_model.Deck.page, mv_model.Deck.index):
        decks.append({
            "name":deck.name,
            "mastervault_link":"https://www.keyforgegame.com/deck-details/"+deck.key
        })
    return {"user":current_user,"decks":decks}

@mvapi.get("/decks/get", tags=["mastervault-clone"])
def deck(key:Optional[str]=None, name:Optional[str]=None, id_:Optional[int]=None):
    print(repr(name))
    session = Session()
    deck = session.query(mv_model.Deck)
    if key:
        deck = deck.filter(mv_model.Deck.key==key)
    if name:
        deck = deck.filter(mv_model.Deck.name==name)
    if id_:
        page = int(id_/24)+1
        index = id_-((page-1)*24)
        print(page,index)
        deck = deck.filter(mv_model.Deck.page==page, mv_model.Deck.index==index)
    print("GET DECK")
    deck = deck.first()
    print("(end)")
    if not deck:
        return "No data"
    cards = [card.aa_format() for card in deck.get_cards()]
    d = {'deck_data':{}}
    d['deck_data'].update(deck.data)
    d['meta'] = {'page':deck.page, 'index':deck.index, 'scrape_date':deck.scrape_date}
    d['cards'] = cards
    return d


@mvapi.get("/decks/walk", tags=["mastervault-clone"])
def decks(start:Optional[int]=None, end:Optional[int]=None):
    if not start: start = 0
    if not end: end = 50
    if start<0:
        start = 0
    if end-start > 1000 or end<start:
        end = start+1000
    if end==start:
        end = start+1
    session = Session()
    total = session.execute("select * from decks_count")
    count = total.first()[0]
    left_bound_page = start//int(24)
    left_bound_index = start-left_bound_page*24
    right_bound_page = end//int(24)
    right_bound_index = end-right_bound_page*24
    left_bound_page += 1
    #left_bound_index += 1
    right_bound_page += 1
    #right_bound_index += 1
    deckq = session.query(mv_model.Deck).\
        filter(mv_model.Deck.page>=left_bound_page,mv_model.Deck.page<=right_bound_page).\
        filter(or_(mv_model.Deck.page<right_bound_page,mv_model.Deck.index<=right_bound_index)).\
        filter(or_(mv_model.Deck.page>left_bound_page,mv_model.Deck.index>=left_bound_index)).\
        order_by(mv_model.Deck.page, mv_model.Deck.index)
    decks = deckq.all()
    return {"start": start, "end": end, "max": count, 
            "bounds": [(left_bound_page, left_bound_index), (right_bound_page, right_bound_index)],
            "count":len(decks),
            "decks":[[d.key, d.name, ", ".join(d.data['_links']['houses']), d.data["expansion"]] for d in decks]}

@mvapi.get('/decks/latest', tags=["mastervault-clone"])
def latest():
    session = Session()
    query = session.execute("select key from decks where (select max(page) from decks)=page order by index desc limit 1;")
    key = query.first()[0]
    return deck(key)

@mvapi.get("/card_query", tags=["mastervault-clone"])
def card_query(
        name:Optional[str]=None,
        houses:Optional[str]=None,
        expansions:Optional[str]=None,
        is_maverick:bool=False,
        is_enhanced:bool=False,
        limit:bool=True
    ):
    is_maverick = {True:'true',False:'false'}[is_maverick]
    is_enhanced = {True:'true',False:'false'}[is_enhanced]
    session = Session()
    cardq = session.query(mv_model.Card)
    if houses:
        houses = [x.strip() for x in houses.split(',')]
        for h in houses:
            cardq = cardq.filter(mv_model.Card.data['house'].has_key(h))
    if expansions:
        expansions = [int(x.strip()) for x in expansions.split(',')]
        cardq = cardq.filter(or_(
            *[mv_model.Card.data['expansion'].astext == str(expansion) for expansion in expansions]
        ))
    if name:
        name = "%{}%".format(name)
        cardq = cardq.filter(mv_model.Card.name.ilike(name))
    cardq = cardq.filter(mv_model.Card.data['is_maverick'].astext == is_maverick)
    cardq = cardq.filter(mv_model.Card.data['is_enhanced'].astext == is_enhanced)
    if limit:
        cardq = cardq.limit(10)
    print(str(cardq))
    cards = cardq.all()
    return {"cards":
        [
            card.aa_format()["card_title"]
            for card in cards
        ]}

@mvapi.post('/user/create', tags=["user-operation"])
def create_user(admin_key:str, email:str, password:str):
    print("insert email",email)
    if admin_key!=passwords.KFDECKSERV_ADMIN_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    session = Session()
    api_user = mv_model.ApiUser(uuid=uuid.uuid4(),email=email, hashed_password=pwd_context.hash(password))
    session.add(api_user)
    session.commit()
    session.close()
    user = get_user(email)
    return user

@mvapi.post('/user/update', tags=["user-operation"])
def update_user(current_user: UserInDB = Depends(get_current_user),
                email:Optional[str]=None, password:Optional[str]=None,
                dok_key:Optional[str]=None):
    session = Session()
    api_user = session.query(mv_model.ApiUser).filter(mv_model.ApiUser.email==current_user.email).first()
    if dok_key:
        api_user.dok_key = dok_key
    if email:
        api_user.email = email
    if password:
        api_user.hashed_password = pwd_context.hash(password)
    session.add(api_user)
    session.commit()
    user = get_user(api_user.email)
    return user

@mvapi.get('/user/decks/get_dok', tags=["user-operation"])
def update_user_decks(current_user: UserInDB = Depends(get_current_user)):
    session = Session()
    api_user = session.query(mv_model.ApiUser).filter(mv_model.ApiUser.email==current_user.email).first()
    dok_decks = dok.get_decks(api_user.dok_key)
    add_decks = []
    for deck in dok_decks:
        add_decks.append(mv_model.OwnedDeck(deck_key=deck['deck']['keyforgeId'], user_key=api_user.uuid))
    mv_model.postgres_upsert(session, mv_model.OwnedDeck, add_decks)
    session.commit()
    return {"updated":len(dok_decks)}


from fastapi import BackgroundTasks
def task_write_aa_deck_to_page(page, deck):
    content = deck_writer.write(deck)
    return page.edit(content, "building deck page")


@mvapi.get('/generate_aa_deck_page', tags=["aa-api"])
def generate_aa_deck_page(key:str=None, recreate=False, background_tasks:BackgroundTasks=None):
    # Check if aa page exists
    wp = connections.get_wiki()
    page = wp.page("Deck:" + key)
    if not recreate:
        page.info()
        if bool(page):
            return {"exists": True, "operation": None}
    # Get deck
    session = Session()
    deck_query = session.query(mv_model.Deck)
    if key:
        deck_query = deck_query.filter(mv_model.Deck.key==key)
    deck = deck_query.first()
    # Create AA page from deck info
    background_tasks.add_task(task_write_aa_deck_to_page, page, deck)
    return {"exists": False, "operation": "edited"}


@mvapi.get('/get_aa_deck_data', tags=["aa-api"])
def get_aa_deck_data(key:str=None):
    # Get deck
    session = Session()
    deck_query = session.query(mv_model.Deck)
    if key:
        deck_query = deck_query.filter(mv_model.Deck.key==key)
    deck = deck_query.first()
    # Return data
    return deck_writer.DeckWriter(deck).deck_json()


@mvapi.get("/deck_query", tags=["aa-api"])
def deck_query(
        name:Optional[str]=None,
        houses:Optional[str]=None,
        expansions:Optional[str]=None,
        key:Optional[str]=None,
        page:Optional[int]=0
    ):
    uuid_re = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)
    if name and uuid_re.findall(name):
        key = uuid_re.findall(name)[0].lower()
        name = None
    session = Session()
    deckq = session.query(mv_model.Deck)
    if houses:
        houses = [x.strip() for x in houses.split(',')]
        for h in houses:
            deckq = deckq.filter(mv_model.Deck.data['_links']['houses'].contains('"'+h+'"'))
    if expansions:
        expansions = [int(x.strip()) for x in expansions.split(',')]
        deckq = deckq.filter(or_(
            *[mv_model.Deck.expansion == expansion for expansion in expansions]
        ))
    if name:
        name = "%{}%".format(
            util.sanitize_deck_name(name)
        )
        deckq = deckq.filter(
            mv_model.Deck.name_sane.ilike(name)
        )
    if key:
        deckq = deckq.filter(
            mv_model.Deck.key==key.strip()
        )
    #deckq = deckq.order_by(mv_model.Deck.page)
    page_size=15
    deckq = deckq.limit(page_size)
    deckq = deckq.offset(page*page_size)
    print(str(deckq))
    decks = deckq.all()
    return {
        "count": len(decks),
        "decks":
        [
            [
                d.key,
                d.name,
                ", ".join(d.houses),
                d.data["expansion"]
            ] for d in decks
        ]}


@mvapi.get("/deck_count", tags=["aa-api"])
def deck_count():
    resp = {}
    session = Session()
    counts = session.query(mv_model.Counts).all()
    for count in counts:
        resp[count.label] = "{:,}".format(count.count)
    return resp


@mvapi.put('/generate_event_decks', tags=["aa-maintenance"])
def generate_event_decks(current_user: UserInDB = Depends(get_current_user)):
    wp = connections.get_wiki()
    import tool_update_decks
    return {"edited": tool_update_decks.update_event_decks(wp)}


mvapi.mount("/static", StaticFiles(directory="mastervault/static"), name="static")
