from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt,JWTError
from datetime import datetime, timedelta
import sys, os, traceback
import base64
from mastervault import datamodel
from sqlalchemy import or_, and_
import carddb
import connections
from mastervault import dok, deck_writer
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "f16861df9f66125336d2f588c080b67f22a0c39267dd5127654b6bc71d9c1bbd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

mvapi = FastAPI()
origins = ["https://archonarcana.com"]
mvapi.add_middleware(
    CORSMiddleware,
    allow_origins=origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*']
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    session = datamodel.Session()
    api_user = session.query(datamodel.ApiUser).filter(datamodel.ApiUser.email==email).first()
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

@mvapi.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password",
                            headers={"WWW-Authenticate":"Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub":user.email}, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@mvapi.get('/mydecks')
async def mydecks(current_user: UserInDB = Depends(get_current_user)):
    decks = []
    session = datamodel.Session()
    print(str(session.query(datamodel.Deck).\
            join(datamodel.OwnedDeck, datamodel.OwnedDeck.deck_key==datamodel.Deck.key).\
            filter(datamodel.OwnedDeck.user_key==str(current_user.uuid)).\
            order_by(datamodel.Deck.page, datamodel.Deck.index)))
    for deck in session.query(datamodel.Deck).\
            join(datamodel.OwnedDeck, datamodel.OwnedDeck.deck_key==datamodel.Deck.key).\
            filter(datamodel.OwnedDeck.user_key==str(current_user.uuid)).\
            order_by(datamodel.Deck.page, datamodel.Deck.index):
        decks.append({
            "name":deck.name,
            "mastervault_link":"https://www.keyforgegame.com/deck-details/"+deck.key
        })
    return {"user":current_user,"decks":decks}

@mvapi.get("/deck")
def deck(key:Optional[str]=None, name:Optional[str]=None, id_:Optional[int]=None):
    print(repr(name))
    session = datamodel.Session()
    deck = session.query(datamodel.Deck)
    if key:
        deck = deck.filter(datamodel.Deck.key==key)
    if name:
        deck = deck.filter(datamodel.Deck.name==name)
    if id_:
        page = int(id_/24)+1
        index = id_-((page-1)*24)
        print(page,index)
        deck = deck.filter(datamodel.Deck.page==page, datamodel.Deck.index==index)
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


@mvapi.get("/deck_query")
def deck_query(
        name:Optional[str]=None,
        houses:Optional[str]=None,
        expansions:Optional[str]=None
    ):
    session = datamodel.Session()
    deckq = session.query(datamodel.Deck)
    if houses:
        houses = [x.strip() for x in houses.split(',')]
        for h in houses:
            deckq = deckq.filter(datamodel.Deck.data['_links']['houses'].has_key(h))
    if expansions:
        expansions = [int(x.strip()) for x in expansions.split(',')]
        deckq = deckq.filter(or_(
            *[datamodel.Deck.expansion == expansion for expansion in expansions]
        ))
    if name:
        name = "%{}%".format(name)
        deckq = deckq.filter(datamodel.Deck.name.ilike(name))
    deckq = deckq.limit(10)
    print(str(deckq))
    decks = deckq.all()
    return {"decks":
        [
            [
                d.key,
                d.name,
                ", ".join(d.data['_links']['houses']),
                d.data["expansion"]
            ] for d in decks
        ]}


@mvapi.get("/decks")
def decks(start:Optional[int]=None, end:Optional[int]=None):
    if not start: start = 0
    if not end: end = 50
    if start<0:
        start = 0
    if end-start > 1000 or end<start:
        end = start+1000
    if end==start:
        end = start+1
    session = datamodel.Session()
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
    deckq = session.query(datamodel.Deck).\
        filter(datamodel.Deck.page>=left_bound_page,datamodel.Deck.page<=right_bound_page).\
        filter(or_(datamodel.Deck.page<right_bound_page,datamodel.Deck.index<=right_bound_index)).\
        filter(or_(datamodel.Deck.page>left_bound_page,datamodel.Deck.index>=left_bound_index)).\
        order_by(datamodel.Deck.page, datamodel.Deck.index)
    decks = deckq.all()
    return {"start": start, "end": end, "max": count, 
            "bounds": [(left_bound_page, left_bound_index), (right_bound_page, right_bound_index)],
            "count":len(decks),
            "decks":[[d.key, d.name, ", ".join(d.data['_links']['houses']), d.data["expansion"]] for d in decks]}

@mvapi.get('/deck/latest')
def latest():
    session = datamodel.Session()
    query = session.execute("select key from decks where (select max(page) from decks)=page order by index desc limit 1;")
    key = query.first()[0]
    return deck(key)

@mvapi.post('/create_user')
def create_user(admin_key:str, email:str, password:str):
    print("insert email",email)
    if admin_key!="tiddlywinks":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid key")
    session = datamodel.Session()
    api_user = datamodel.ApiUser(uuid=uuid.uuid4(),email=email, hashed_password=pwd_context.hash(password))
    session.add(api_user)
    session.commit()
    session.close()
    user = get_user(email)
    return user

@mvapi.post('/update_user')
def update_user(current_user: UserInDB = Depends(get_current_user),
                email:Optional[str]=None, password:Optional[str]=None,
                dok_key:Optional[str]=None):
    session = datamodel.Session()
    api_user = session.query(datamodel.ApiUser).filter(datamodel.ApiUser.email==current_user.email).first()
    if dok_key:
        api_user.dok_key = dok_key
    session.add(api_user)
    session.commit()
    user = get_user(api_user.email)
    return user

@mvapi.get('/update_decks')
def update_user_decks(current_user: UserInDB = Depends(get_current_user)):
    session = datamodel.Session()
    api_user = session.query(datamodel.ApiUser).filter(datamodel.ApiUser.email==current_user.email).first()
    dok_decks = dok.get_decks(api_user.dok_key)
    add_decks = []
    for deck in dok_decks:
        add_decks.append(datamodel.OwnedDeck(deck_key=deck['deck']['keyforgeId'], user_key=api_user.uuid))
    datamodel.postgres_upsert(session, datamodel.OwnedDeck, add_decks)
    session.commit()
    return {"updated":len(dok_decks)}

@mvapi.get('/generate_aa_deck_page')
def generate_aa_deck_page(key:str=None, recreate=False):
    # Check if aa page exists
    wp = connections.get_wiki()
    page = wp.page("Deck:" + key)
    if not recreate:
        page.info()
        if bool(page):
            return {"exists": True, "operation": None}
    # Get deck
    session = datamodel.Session()
    deck_query = session.query(datamodel.Deck)
    if key:
        deck_query = deck_query.filter(datamodel.Deck.key==key)
    deck = deck_query.first()
    # Create AA page from deck info
    content = deck_writer.write(deck)
    result = page.edit(content, "building deck page") 
    return {"exists": False, "operation": result.get("edit")}


mvapi.mount("/static", StaticFiles(directory="mastervault/static"), name="static")