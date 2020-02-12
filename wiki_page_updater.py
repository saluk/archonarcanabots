import wikitextparser as wtp
import re
import time
import json
import os
import difflib
import requests
import connections
import carddb

# TODO - add templates to appropriate pages
# TODO - create artist pages that list their cards

wp = connections.get_wiki()

category_markup = re.compile("\[\[Category:(\w| |-)+\]\]")
section_header = re.compile("^=+([\w ]+)=+", re.MULTILINE)
wikitable_row = re.compile("^\|-", re.MULTILINE)
wikitable = re.compile("\{\|(.|\n)*")

SETS = {452: "WC", 453: "WC-A", 341: "CotA", 435: "AoA"}
SET_BY_NUMBER = {}
SET_ORDER = []
for numerical_set in sorted(SETS.keys()):
    setname = SETS[numerical_set]
    SET_ORDER.append(setname)
    SET_BY_NUMBER[setname] = numerical_set

HIGHEST_SET_LOCAL_IMAGE = 452


class Section(object):
    def __init__(self, contents):
        self.name = None
        self.contents = contents.replace("\r\n", "\n").replace("\r", "\n")
        self.contents = self.contents.strip()
        title = section_header.search(self.contents)
        if title:
            self.name = self.contents[title.start():title.end()]
        self.data = {}
        self.categories = set()
        self.get_data()

    def delete_category_markup(self, text):
        return category_markup.sub("", text)
    
    def clean_category(self, category):
        return category.replace(" ", "_")

    def get_data(self):
        title = section_header.search(self.contents)
        if not title:
            self.data["text"] = self.contents.strip()
            self.data["header"] = None
            return
        header = self.contents[title.start():title.end()].strip()
        rest = self.contents[title.end():].strip()
        rest = self.delete_category_markup(rest).strip()
        self.data["text"] = rest
        self.data["title"] = self.contents[title.start(1):title.end(1)].strip()
        self.data["header"] = header
        self.categories = set([self.clean_category(self.data["title"])])

    def output_text(self):
        return self.data["text"]

    def output_categories(self):
        def to_cat_str(cat):
            return "[[Category:%s]]" % cat.strip()
        sort_cats = sorted(list(self.categories))
        return "".join([to_cat_str(x) for x in sort_cats])

    def output(self):
        text = ""
        if self.data["header"]:
            text += "\n" + self.data["header"] + "\n\n"
        text += self.output_text() + "\n"
        text += self.output_categories()
        return text


class CardSection(Section):

    def add_set(self, setname, setnum):
        if "sets" not in self.data:
            self.data["sets"] = {}
        self.data["sets"][setname] = setnum

    def add_traits(self, traits):
        traits = re.findall("\w+", traits)
        self.data["traits"] = traits

    def add_stat(self, stat, value):
        if not value:
            return
        if type(value) == str:
            if not value.isdigit():
                return
            value = int(value)
        if value > 0:
            self.data[stat] = str(value).strip()

    def process_image(self, image):
        if image.endswith("png") or image.endswith("jpg"):
            self.data["image"] = image.strip()
            return
        for link in wtp.parse(image).external_links:
            if link.text.endswith(".png") or link.text.endswith(".jpg"):
                self.data["image"] = link.text.strip()
                self.data["image_url"] = link.url.strip()
                return
        for link in wtp.parse(image).wikilinks:
            if link.target.endswith(".png") or link.target.endswith(".jpg"):
                self.data["image"] = link.target
        self.data["image"] = ""
        self.data["table_original"].append(("image", image))

    def process_field_value(self, value):
        val = wtp.parse(value)
        if val.wikilinks:
            if value.strip() == str(val.wikilinks[0]).strip():
                return val.wikilinks[0].text.strip()
        return str(val).strip()

    def process_field(self, row):
        key, val = row
        key = key.lower().strip().replace(" ", "_")
        if key.startswith("sets"):
            key = "sets"
        print("PROCESS",key,val)
        if key == "sets":
            for setd in val.split(","):
                num_in_paren = re.compile(".*\((.+)\)")
                setnum = num_in_paren.search(setd).group(1).strip()
                nametext = re.search("(.*)\(", setd).group(1)
                setname = self.process_field_value(nametext)
                self.add_set(setname, setnum)
            if key not in self.data:
                self.data["table_original"].append((key, val))
        elif key and key not in self.data:
            processed = self.process_field_value(val)
            if not processed:
                return
            self.data[key] = processed
            self.data["table_original"].append((key, val))

    def process_artist(self, cell):
        if "artist" in self.data:
            return
        print("PROCESSING ARTIST")
        self.data["artist"] = cell.strip()
        self.data["table_original"].append(("artist", cell))

    def process_table(self, table):
        table_parsed = wtp.parse(table)
        table1 = table_parsed.tables[0]
        rows = table1.data(span=False)
        for row in rows:
            if len(row) == 1 and "artist" in row[0].lower():
                self.process_artist(row[0])
            elif not self.data.get("image", None) and len(row) == 1:
                self.process_image(row[0])
            elif(len(row) == 2):
                self.process_field(row)
        before = table[:table1.span[0]]
        after = table[table1.span[1]:]
        self.data["before_table"] = before.strip()
        self.data["after_table"] = after.strip()

    def get_data(self):
        rest = self.delete_category_markup(self.contents).strip()
        self.data["header"] = None
        self.data["table_original"] = []
        self.process_table(wikitable.search(rest).group(0))
        print(self.data)
        return ""

    def link_category(self, text):
        return "[[:Category:%(text)s|%(text)s]]" % {"text":text}

    def link_search(self, text):
        template = '''
<span class="plainlinks">
[https://archonarcana.com/index.php?search=%%22%(textm)s%%22&title=Special%%3ASearch&go=Go %(text)s]
</span>'''
        return template % {"text": text, "textm": text.replace(":", "%3A")}

    def output_image(self):
        setnum = max([SET_BY_NUMBER[name] 
                      for name in self.data["sets"].keys()])
        cardnum = self.data["sets"][SETS[setnum]]
        return "{{CardImage|%s-%s}}" % (setnum, cardnum)

    def output_categories(self):
        def to_cat_str(cat):
            return "[[Category:%s]]" % cat.strip()
        cats = []
        for category_field in ["type", "house", "traits", "rarity", "sets"]:
            data = self.data.get(category_field, None)
            if not data:
                continue
            if category_field == "traits":
                cats.extend(data)
            elif category_field == "sets":
                cats.extend([k for k in data.keys()])
            else:
                cats.append(data)
        #print(self.data.get("card_title", "no_title"))
        #print(self.data.get("card_text", ""))
        if self.data.get("card_title", "no_title") in self.data.get("card_text", ""):
            cats.append("Self-referential")
        cats.sort()
        return "".join([to_cat_str(x) for x in cats])+"\n[[Category:Card]]"

    def output_set_text(self):
        set_texts = []
        for set_name in sorted(self.data["sets"],
                               key = lambda k: SET_ORDER.index(k)):
            set_num = self.data["sets"][set_name]
            set_texts.append(self.link_category(set_name)+"(%s)" % set_num)
        return ", ".join(set_texts)

    def output_stat_text(self):
        texts = []
        for stat_name in ["amber", "power", "armor"]:
            if stat_name in self.data:
                text = stat_name.capitalize() + ":%s" % self.data[stat_name]
                text = self.link_search(text)
                texts.append(text)
        return " ".join(texts)

    def output_text(self):
        text = ""
        if self.data.get("before_table"):
            text = self.data["before_table"] + "\n"
        text += """{| class="wikitable" width = "575" float: right
! colspan = "2" style="text-align: center;"|"""
        ROWMARKUP = """|-
        | style="text-align: center; font-weight:bold;" | %s
        | style="text-align: center;" |%s
        """

        keys = ["image", "artist", "card_text", 
                "updated_text", "flavor_text", "stats",
                "type", "house", "traits", "rarity", "sets"]
        mask_fields = {"updated_text": "card_text"}
        original_data = {}
        for row in self.data["table_original"]:
            original_data[row[0]] = row[1]
        for mask in mask_fields:
            masked = mask_fields[mask]
            if mask in self.data:
                if mask_fields[mask] in self.data:
                    del self.data[masked]
                    keys.remove(masked)

        for key in keys:
            if key not in self.data and key not in original_data:
                continue
            key_output = " ".join([l.capitalize() for l in key.split("_")])
            if key == "image":
                text += self.output_image()+"\n"
            elif key == "artist":
                text += """|-
| colspan = "2" style="text-align: center;"|%(artist)s
""" % self.data
            elif key == "card_text":
                text += ROWMARKUP % ("Card Text", self.data["card_text"])

            elif key == "flavor_text":
                text += ROWMARKUP % ("Flavor Text", self.data["flavor_text"])

            elif key == "stats":
                stat_text = self.output_stat_text()
                if stat_text:
                    text += ROWMARKUP % ("Stats", stat_text)

            elif key == "type":
                text += ROWMARKUP % ("Type", self.link_category(self.data["type"]))

            elif key == "house":
                text += ROWMARKUP % ("House", self.link_category(self.data["house"]))
        
            elif key == "traits":
                text += ROWMARKUP % ("Traits", ", ".join(self.link_category(trait) for trait in self.data["traits"]))

            elif key == "rarity":
                text += ROWMARKUP % ("Rarity", self.link_category(self.data["rarity"]))

            elif key == "sets":
                text += ROWMARKUP % ("Sets", self.output_set_text())

            else:
                val = original_data[key]
                print("export unknown key", key)
                text += ROWMARKUP % (key_output, val)

        text += "|}"
        if self.data.get("after_table"):
            text += "\n\n"+self.data["after_table"]
        return text


class CardPage(object):

    def __init__(self):
        self.sections = []

    def add_section(self, text):
        if not self.sections:
            self.sections.append(CardSection(text))
        else:
            self.sections.append(Section(text))
    
    def from_text(self, text):
        self.sections = []
        start = 0
        for match in section_header.finditer(text):
            self.add_section(text[start:match.start()])
            start = match.start()
        self.add_section(text[start:len(text)])
        #print("\nSTART\n"+"\n".join([x.strip() for x in self.sections[0].delete_category_markup(text).strip().split("\n")]))
        #print("\nOUTPUT\n"+self.sections[0].delete_category_markup(self.output()).strip())
        #assert "\n".join([x.strip() for x in self.sections[0].delete_category_markup(text).strip().split("\n")]) == self.sections[0].delete_category_markup(self.output()).strip()
        return self
    
    def output(self):
        return "\n".join([s.output() for s in self.sections])

    def edit_card_field(self, field, value1, value2=None):
        if field == "sets":
            assert value2
            self.sections[0].add_set(value1, value2)
        elif field == "traits":
            if not value1:
                return
            self.sections[0].add_traits(value1)
        elif field == "card_title":
            self.sections[0].data["card_title"] = value1
        elif field in ["house", "type", "rarity", "card_text"]:
            self.sections[0].data[field] = value1
        else:
            self.sections[0].add_stat(field, value1)


def to_cat_str(cat):
    return "[[Category:%s]]" % cat.strip()


def modify_card_text(text):
    text = re.sub("(\d+)D", r"\1 damage", text)
    text = re.sub(" A ", " aember ", text)
    text = re.sub("(\d+)A", r"\1 aember", text)
    return text


def safe_name(name):
    #if name == "Ortannu’s Binding" or name == "Nature’s Call":
    #    return name.replace("’", "'")
    return name


NO_SAVE = 0
SAVE_SANDBOX = 1
SAVE_FULL = 2


def create_card_page(card, load_existing=True, update_mode=NO_SAVE,
                     update_reason="Script testing",
                     pull_from_sandbox=False):
    card["card_title"] = safe_name(card["card_title"])
    card["card_text"] = modify_card_text(card["card_text"])
    card["card_set"] = card["sets"]
    if card.get("is_anomaly", False):
        card["house"] = "Anomaly"

    if not pull_from_sandbox:
        page = wp.page(card["card_title"])
    else:
        page = wp.page("User:Saluk/Sandbox")
    existing = ""
    if(load_existing):
        try:
            existing = page.read()
        except:
            raise
            existing = ""
            print("missing:", card["card_title"])

    card_page = CardPage().from_text(existing)
    card_page.edit_card_field("card_title", card["card_title"])
    card_page.edit_card_field("card_text", card["card_text"])
    card_page.edit_card_field("traits", card["traits"])
    for exp in card["sets"]:
        card_page.edit_card_field("sets", exp[0], exp[1])
    card_page.edit_card_field("armor", card["armor"])
    card_page.edit_card_field("power", card["power"])
    card_page.edit_card_field("amber", card["amber"])
    card_page.edit_card_field("house", card["house"])
    card_page.edit_card_field("type", card["card_type"])
    card_page.edit_card_field("rarity", card["rarity"])
    card_page.edit_card_field("image", card["front_image"])
    print(card_page.sections[0].data)
    print("outputing")
    card_text = card_page.output()

    if card_text == existing:
        return

    #print(repr(existing),repr(card_text))
    print("\n".join(difflib.unified_diff([existing],[card_text])))
    print("edited", card["card_title"])
    if(update_mode==SAVE_FULL):
        page.edit(card_text, update_reason)
    elif(update_mode==SAVE_SANDBOX):
        sandbox = wp.page("User:Saluk/Sandbox")
        sandbox.edit(card_text, update_reason)
    else:
        pass
    time.sleep(0.05)
    return True



cards = carddb.cards

collect_latest_card = carddb.collect_latest_card


def update_cards(search_name=None, update_mode=NO_SAVE,
                 update_reason="Script testing",
                 pull_from_sandbox=False):
    changed = 0
    for i, card_name in enumerate(cards):
        card = collect_latest_card(card_name)
        if search_name and search_name.lower() not in card_name.lower():
            continue
        print(i+1, card_name)
        if create_card_page(card, load_existing=True,
                            update_mode=update_mode,
                            update_reason=update_reason,
                            pull_from_sandbox=pull_from_sandbox):
            changed += 1
    print(changed, "cards changed")


def update_category_search_pages():

    gallery_template = """
<gallery widths=250 heights=350px>
%s
</gallery>"""
    image_template = """%(file)s|link=[[%(title)s]]"""

    for category in ['CotA', 'WC', 'AoA', 'WC-A',
                     'Brobnar', 'Saurian', 'Dis',
                     'Logos', 'Untamed', 'Shadows',
                     'Star Alliance', 'Sanctum', 'Mars',
                     'Anomaly']:
        print(category)

        card_pages = []
        #for _page in wp.category(category).categorymembers():
        #    house = list(cards[_page.title].values())[0]["house"]
        #    img = list(_page.images())[0]
        #    card_pages.append({"file": img.title.split(":", 1)[1],
        #                       "title": _page.title,
        #                       "house": house})

        #card_pages.sort(key=lambda c: (c["house"], c["title"]))
        #images = [image_template % card for card in card_pages]
        #gallery = gallery_template % "\n".join(images)

        page = wp.page("Category:"+category)
        existing = page.read()
        existing = re.sub('\<gallery.*?\>(.|\n)*?\<\/gallery\>', '', existing, re.MULTILINE)
        existing = existing.strip()
        #existing += "\n" + gallery
        print(existing)
        page.edit(existing, "removing gallery from category pages")
        
def find_card_not_a_card():
    for page in wp.category("Card").categorymembers():
        page_title = page.title
        if page_title not in cards:
            print(page_title)

def list_traits():
    begin = False
    traits = set()
    for i, card_name in enumerate(cards):
        card = collect_latest_card(card_name)
        if not card["traits"]: continue
        for trait in re.findall("\w+", card["traits"]):
            traits.add(trait)
    for trait in traits:
        print(trait)

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


def set_protected(page):
    print("update permissions for page", page.title)
    result = page.protect({'edit': 'sysop', 'move': 'sysop'}, cascade=True)
    print(result)
    time.sleep(0.10)


def set_protections():
    for category in ["Card", "Glossary", "Rules", "Tournament Rules"]:
        cat = wp.category(category)
        for page in cat.categorymembers():
            set_protected(page)


#update_cards("life for a life", update_mode=SAVE_SANDBOX, pull_from_sandbox=False)
#markup("User:Saluk/Sandbox")
#set_protections()
p = wp.page("Library_Access")
print(dir(p))
print(p.info())
print(p.info()['pageid'])
