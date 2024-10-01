import os
import connections
wp = connections.get_wiki()
from util import cargo_query
import requests
import re
import json
from models import shared

lasthashes = {}
if os.path.exists("cache/lasthash.json"):
    with open("cache/lasthash.json") as f:
        try:
            lasthashes = json.loads(f.read())
        except Exception:
            pass

def make_search_kfa(search, limit_set):
    if "CardData" in search["tables"]:
        search["tables"] += ",SetData,SetInfo"
        search["join_on"] = "SetData.Setname=SetInfo.Setname, SetData._pageName=CardData._pageName"
        #search["fields"] += ",SetInfo.SetNumber"
        if limit_set:
            search["where"] = f"SetInfo.SetName = '{limit_set}'"
        else:
            search["where"] = "SetInfo.SetNumber not like '%KFA%'"

def gen_artists(tables, limit_set=None):
    search = {
        "tables": tables,
        "fields": "Artist",
        "group_by": "Artist"
    }
    make_search_kfa(search, limit_set)
    artists = []
    for result in cargo_query(search)['cargoquery']:
        if not result['title'] or not 'Artist' in result['title']:
            continue
        if not result['title']['Artist']:
            continue
        a = result['title']['Artist'].replace("?","").strip()
        if not a or a in artists:
            continue
        artists.append(a)
    artists.sort()
    return artists

def load_data():
    f = open("javascript/data_t.js")
    lines = f.readlines()
    keys = {}
    for l in lines:
        if l.startswith("var"):
            k = l.split(" ")[1]
            try:
                v = eval(l.split("=", 1)[1].strip())
            except:
                continue
            keys[k] = v
    return keys
data_t = load_data()

def gen_artists_by_set():
    d = {}
    for set in data_t["sets"]:
        artists = gen_artists("CardData", set.replace("_", " "))
        d[set] = artists
    return d

def gen_traits_by_set():
    d = {}
    for set in data_t["sets"]:
        traits = gen_traits("CardData", set.replace("_", " "))
        d[set] = traits
    return d


def gen_traits(tables, limit_set=None):
    search = {
        "tables": tables,
        "fields": "Traits",
        "group_by": "Traits"
    }
    make_search_kfa(search, limit_set)
    traits = []
    for result in cargo_query(search)['cargoquery']:
        if not result['title'] or not 'Traits' in result['title']:
            continue
        if not result['title']['Traits']:
            continue
        for t in result['title']['Traits'].split(" • "):
            t = t.replace('?','').strip()
            if not t or t in traits:
                continue
            traits.append(t)
    traits.sort()
    return traits


def get_kfa_sets():
    search = {
        "tables": "SetInfo",
        "fields": "SetInfo.SetName",
        "where": "SetInfo.SetNumber like '%KFA%'"
    }
    for result in cargo_query(search)['cargoquery']:
        yield result['title']['SetName']
kfa_sets = list(get_kfa_sets())


def gen_artists_kfa():
    artists_by_set = {}
    for s in kfa_sets:
        artists_by_set[s.replace(" ","_")] = gen_artists("CardData", s)
    return json.dumps(artists_by_set)
artists_kfa = gen_artists_kfa()


def gen_traits_kfa():
    traits_by_set = {}
    print(kfa_sets)
    for s in kfa_sets:
        traits_by_set[s.replace(" ","_")] = gen_traits("CardData", s)
    return json.dumps(traits_by_set)
traits_kfa = gen_traits_kfa()


def gen_card_combos():
    p = wp.page('Essay:List_of_Keyforge_Combos')
    combos = []
    for combo in re.findall(r'[*] .*?$', p.content, re.MULTILINE):
        combos.append(re.findall(r'\[\[(.*?)\]\]', combo))
    return combos

#print(gen_card_combos())

hashes = {}

def hash_filename(filename, txt):
    import base64
    import hashlib
    hasher = hashlib.sha1((filename+txt).encode('utf8'))
    part = base64.urlsafe_b64encode(hasher.digest()[:10])
    return filename.replace('.js','_')+part.decode('utf8')+'.js'

def upload_js_file(filename, use_hash=True, test=False):
    with open("javascript/"+filename) as f:
        txt = f.read()
        if '<HASH_ME>' in txt or use_hash:
            hashes[filename] = hash_filename(filename, txt)
            wpname = "MediaWiki:"+hashes[filename]
        else:
            wpname = "MediaWiki:" + filename
        print(wpname)
        if not test:
            page = wp.page(wpname)
            print(page.edit(txt, "javascript updated"))

def upload(stage="dev", test=False):
    assert stage in ['dev', 'prod']
    with open("javascript/data_t.js") as f:
        gen_data = f.read()
        reps = {
            "//CARDCOMBOS": "var cardCombos = %s" % "[]" # repr(gen_card_combos())
        }
        for r in reps:
            gen_data = gen_data.replace(r, reps[r])
    with open("javascript/data.js","w") as f:
        f.write(gen_data)
    os.system("npm run build -- --mode=%s" % {
        "prod": "production",
        "dev": "development"
    }[stage])
    for bundle in [
        "main.indexCommon.js",
        "main.indexDeckSearch.js",
        "main.indexDeckView.js",
        "main.indexGallery.js",
        "main.indexQuick.js"
    ]:
        os.system("scp javascript/{} saluk@archonarcana.com:/var/www/html/{}/extensions/AADeckView/resources/ext.aaDeckView".format(
            bundle, {"prod":"aa-en", "dev":"aa-en"}[stage]
        ))
    upload_js_file("cardwidget.js", use_hash=False, test=test)
    for filename in ['Common.js', 'Mobile.js']:
        with open("javascript/"+filename) as f:
            txt = f.read()
            hashkey = "<FILENAME_%s>"
            debughashkey = "<FILENAMEDEBUG_%s>"
            for hashed in hashes:
                lastk = hashkey % hashed
                k = debughashkey % hashed
                print(lastk,k)
                if lastk in txt:
                    if hashed in lasthashes and stage == "dev":
                        txt = txt.replace(lastk, lasthashes[hashed])
                        print("REPLACE LASTHASH", lastk, lasthashes)
                    else:
                        txt = txt.replace(lastk, hashes[hashed])
                        print("REPLACE HASH", lastk, hashes)
                if k in txt:
                    print("REPLACE HASH", k, hashes)
                    txt = txt.replace(k, hashes[hashed])
            wpname = "MediaWiki:" + filename
            print(txt)
            if not test:
                page = wp.page(wpname)
                print(txt)
                print(page.edit(txt, "javascript updated"))
    if not test and stage == "prod":
        with open("cache/lasthash.json", "w") as f:
            f.write(json.dumps(hashes))
