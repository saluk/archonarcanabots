def quotify(s):
    lq = "“"
    rq = "”"
    parse = s.split('"')
    new = ""
    next = [lq,rq]
    while len(parse)>=2:
        new += parse.pop(0)
        q = next.pop(0)
        next.append(q)
        new += q
    while parse:
        new += parse.pop(0)
    return new

cache = {}
if os.path.exists("mv.cache"):
    with open("mv.cache") as f:
        cache = json.loads(f.read())
def master_vault_lookup(deck_name):
    url = "https://www.keyforgegame.com/api/decks/"
    args = {
        "page": 1,
        "page_size": 10,
        "search": deck_name,
        "power_level": "0,11",
        "chains": "0,24",
        "ordering": "-date"
    }
    key = url+";params:"+json.dumps(args, sort_keys=True)
    if key not in cache:
        time.sleep(4)
        r = requests.get(url, params=args)
        j = r.json()
        if j.get("code", None) == 429:
            raise(Exception(j["message"]+";"+j["detail"]))
        cache[key] = j
        with open("mv.cache", "w") as f:
            f.write(json.dumps(cache))
    dat = cache[key]
    if "data" not in dat:
        raise Exception("No data found", key)
    if len(dat["data"])>1:
        raise Exception("Too many decks found")
    if not dat["data"]:
        quoted = quotify(deck_name)
        if quoted!=deck_name:
            return master_vault_lookup(quoted)
        raise Exception("No deck found", key)
    deck_dat = dat["data"][0]
    return {
        "url": "https://www.keyforgegame.com/deck-details/%(id)s" % {"id": deck_dat["id"]}
    }

def markup(page_name):
    p = wp.page(page_name)
    existing = p.read()
    lines = existing.split('\n')
    new = []
    while lines:
        next = lines.pop(0)
        new.append(next)
        if "<!-- mvdecklink " in next:
            alter_line = lines.pop(0)
            parse = wtp.parse(alter_line)
            for l in parse.external_links:
                print(l.text, l.url)
                url = master_vault_lookup(deck_name=l.text)["url"]
                l.url = url
            new.append(parse.pprint())
    updated = "\n".join(new)
    if updated!=existing:
        p.edit(updated,"deck lookups")