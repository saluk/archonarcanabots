import re
from wikibase import Section, to_cat_str, wikitable, section_header
import wikitextparser as wtp
import carddb


class CardSection(Section):
    def add_set(self, setname, setnum):
        if "sets" not in self.data:
            self.data["sets"] = {}
        self.data["sets"][setname] = setnum

    def add_traits(self, traits):
        traits = re.findall(r"\w+", traits)
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
        if key == "sets":
            for setd in val.split(","):
                num_in_paren = re.compile(r".*\((.+)\)")
                setnum = num_in_paren.search(setd).group(1).strip()
                nametext = re.search(r"(.*)\(", setd).group(1)
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
        return ""

    def link_category(self, text):
        return "[[:Category:%(text)s|%(text)s]]" % {"text": text}

    def link_search(self, text):
        template = '''
<span class="plainlinks">
[https://archonarcana.com/index.php?search=%%22%(textm)s%%22&title=Special%%3ASearch&go=Go %(text)s]
</span>'''
        return template % {"text": text, "textm": text.replace(":", "%3A")}

    def output_image(self):
        setnum = max([carddb.SET_BY_NUMBER[name]
                      for name in self.data["sets"].keys()])
        cardnum = self.data["sets"][carddb.SETS[setnum]]
        return "{{CardImage|%s-%s}}" % (setnum, cardnum)

    def output_categories(self):
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
        if self.data.get("card_title", "no_title") in self.data.get("card_text", ""):
            cats.append("Self-referential")
        cats.sort()
        return "".join([to_cat_str(x) for x in cats])+"\n[[Category:Card]]"

    def output_set_text(self):
        set_texts = []
        for set_name in sorted(self.data["sets"],
                               key=lambda k: carddb.SET_ORDER.index(k)):
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

    def build_from_card(self, card):
        self.edit_card_field("card_title", card["card_title"])
        self.edit_card_field("card_text", card["card_text"])
        self.edit_card_field("traits", card["traits"])
        for exp in card["sets"]:
            self.edit_card_field("sets", exp[0], exp[1])
        self.edit_card_field("armor", card["armor"])
        self.edit_card_field("power", card["power"])
        self.edit_card_field("amber", card["amber"])
        self.edit_card_field("house", card["house"])
        self.edit_card_field("type", card["card_type"])
        self.edit_card_field("rarity", card["rarity"])
        self.edit_card_field("image", card["front_image"])


class CardQuerySection(Section):
    def output(self):
        return "{{Card Query}}\n"


def pull_artist(card, ct, wp):
    card = carddb.get_latest_from_card(card)
    old_page = wp.page(card["card_title"])
    card_page = CardPage()
    card_page.from_text(old_page.read())
    artist = card_page.sections[0].data["artist"]
    artist = re.sub(r"artist\:", "", artist, flags=re.IGNORECASE)
    wikilinks = wtp.parse(artist).wikilinks
    if wikilinks:
        artist = wikilinks[0].target
    artist = artist.strip()
    ct.update_or_create("CardData", card["card_title"], {
        "Artist": artist
    })


def replace_old_card_text(card_title, ot):
    card_page = CardPage()
    card_page.from_text(ot)
    card_page.sections[0] = CardQuerySection("")
    for i, section in enumerate(card_page.sections[:]):
        if section.name:
            if section.name.replace("=","").lower().strip() not in [
                "faq",
                "unofficial faq",
                "commentary",
                "references"
            ]:
                del card_page.sections[i]
    text = card_page.output()
    text = text.replace("{{SEO}}", "")
    return text


if __name__=="__main__":
    import connections
    wp = connections.get_wiki()
    # ct = wikibase.CargoTable()
    replace_old_card_text("Bait and Switch", wp)
