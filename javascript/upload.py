import os
import connections
wp = connections.get_wiki()
import requests

lasthashes = {"main.js":"main_Fx9P3SZh5154dg==.js"}

def cargo_query(search_params):
    start = "/api.php?action=cargoquery&format=json"
    params = {
        "action":"cargoquery",
        "format":"json",
    }
    params.update(search_params)
    r = requests.get("https://archonarcana.com/api.php", params=params)
    return r.json()

cache = {}

def gen_artists(tables):
    k = "gen_artists_"+tables
    if k in cache:
        return cache[k]
    search = {
        "tables":tables,
        "fields":"Artist",
        "group_by":"Artist"
    }
    artists = []
    for result in cargo_query(search)['cargoquery']:
        a = result['title']['Artist'].replace("?","").strip()
        if not a or a in artists: continue
        artists.append(a)
    cache[k] = artists
    return artists

def gen_traits(tables):
    k = "gen_traits_"+tables
    if k in cache:
        return cache[k]
    search = {
        "tables":tables,
        "fields":"Traits",
        "group_by":"Traits"
    }
    traits = []
    for result in cargo_query(search)['cargoquery']:
        for t in result['title']['Traits'].split(" • "):
            t = t.replace('?','').strip()
            if not t or t in traits: continue
            traits.append(t)
    cache[k] = traits
    return traits

hashes = {}

def hash_filename(filename, txt):
    import base64
    import hashlib
    hasher = hashlib.sha1((filename+txt).encode('utf8'))
    part = base64.urlsafe_b64encode(hasher.digest()[:10])
    return filename.replace('.js','_')+part.decode('utf8')+'.js'

def upload_js_file(filename, use_hash=True):
    with open("javascript/"+filename) as f:
        txt = f.read()
        if '<HASH_ME>' in txt or use_hash:
            hashes[filename] = hash_filename(filename, txt)
            wpname = "MediaWiki:"+hashes[filename]
        else:
            wpname = "MediaWiki:" + filename
        print(wpname)
        page = wp.page(wpname)
        print(page.edit(txt, "javascript updated"))

def upload():
    with open("javascript/data_t.js") as f:
        gen_data = f.read()
        reps = {
            "//ARTISTS": "var artists = %s" % repr(gen_artists("CardData")),
            "//SET5ARTISTS": "var set5artists = %s" % repr(gen_artists("SpoilerData")),
            "//TRAITS": "var traits = %s" % repr(gen_traits("CardData")),
            "//SET5TRAITS": "var set5traits = %s" % repr(gen_traits("SpoilerData"))
        }
        for r in reps:
            gen_data = gen_data.replace(r, reps[r])
    with open("javascript/data.js","w") as f:
        f.write(gen_data)
    os.system("npm run build")
    upload_js_file("main.js")
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
                    txt = txt.replace(lastk, lasthashes[hashed])
                if k in txt:
                    txt = txt.replace(k, hashes[hashed])
            wpname = "MediaWiki:" + filename
            page = wp.page(wpname)
            print(txt)
            print(page.edit(txt, "javascript updated"))
