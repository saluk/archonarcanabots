import re, os, difflib, json

category_markup = re.compile(r"\[\[Category:(\w| |-)+\]\]")
section_header = re.compile(r"^=+([\w ]+)=+", re.MULTILINE)
wikitable_row = re.compile(r"^\|-", re.MULTILINE)
wikitable = re.compile(r"\{\|(.|\n)*")


skip_status = {}
if os.path.exists("skips.json"):
    with open("skips.json") as f:
        skip_status = json.loads(f.read())
def add_skip(name):
    skip_status[name] = {"skipped":True}
    with open("skips.json", "w") as f:
        f.write(json.dumps(skip_status))


def update_page(title, page, text, reason, ot,
                pause=False, read=False, only_new_edits=False):
    if title in skip_status:
        print("skipping", title)
        return
    if read or only_new_edits:
        try:
            ot = page.read()
            if only_new_edits:
                return
        except:
            pass
    if text != ot and pause:
        print("DIFF")
        for l in difflib.context_diff(ot.split("\n"), text.split("\n")):
            print(l)
        print("Changing", title)
        cont = input("(k)eep, (upd)ate, or anything else to ask later:")
        if cont == "k":
            add_skip(title)
        if cont != "upd":
            return
    if text == ot:
        return None

    update = page.edit(text, reason).get("edit", {"nochange": ""})
    if "nochange" in update:
        return None


def to_cat_str(cat):
    return "[[Category:%s]]" % cat.strip()


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
        sort_cats = sorted(list(self.categories))
        return "".join([to_cat_str(x) for x in sort_cats])

    def output(self):
        text = ""
        if self.data["header"]:
            text += "\n" + self.data["header"] + "\n\n"
        text += self.output_text() + "\n"
        text += self.output_categories()
        return text


def cargo_index(table_type):
    return {"CardData": ["Name"],
            "CardLocaleData": ["EnglishName", "Locale"],
            "SetData": ["SetName"],
            "TranslationTable": ["EnglishText", "Locale"]}.get(table_type, "default")


def cargo_unique(datatype):
    return {"ErrataData": ("Version", "Text")}.get(datatype, None)


def cargo_sort(table_type, table):
    from models import shared
    sort_function = {
        "SetData": lambda row: shared.set_data.sort_order(row["SetName"]),
        "AltArt": lambda row: (int(row["Year"]), row["File"])
    }.get(table_type, None)
    if sort_function:
        return sorted(table, key=sort_function)
    defkey = cargo_index(table_type)
    if defkey:
        return sorted(table, key=lambda row: tuple([row.get(k, '') for k in defkey]))
    return table


class CargoTable:
    def __init__(self, page_name=""):
        self.data_types = {}  #Each data type is a different cargo table
        self.page_name = page_name  #All datatypes are written to this page name

    def read_from_text(self, text):
        d = {}
        TYPE = 1
        ROW = 2
        mode = TYPE
        text = re.sub("}}( *){{", "}}\n{{", text)
        last_key = ""
        for line in text.split("\n"):
            #print("\t\t", line)
            if mode == TYPE:
                if line.startswith("{{"):
                    d["type"] = line[2:]
                    mode = ROW
                    continue
            elif mode == ROW:
                if line.startswith("|"):
                    left, right = line.split("=", 1)
                    last_key = left[1:]
                    d[last_key] = right
                elif line.startswith("}}"):
                    datatype = d["type"]
                    del d["type"]
                    if datatype not in self.data_types:
                        self.data_types[datatype] = {}
                    index_key = cargo_index(datatype)
                    if index_key != "default":
                        key = tuple([d[x] for x in index_key])
                        if len(key) == 1:
                            key = key[0]
                    else:
                        key = len(self.data_types[datatype])
                    self.data_types[datatype][key] = d
                    d = {}
                    mode = TYPE
                else:
                    if last_key:
                        d[last_key] += "\n"+line

    def output_text(self):
        print("before output:", self.data_types)
        def write_item(item, datatype):
            t = "{{%s\n" % datatype
            for k in item:
                v = item[k] if item[k]!=None else ""
                t += "|%s=%s\n" % (k, v)
            t += "}}"
            return t
        t = ""
        for datatype in self.data_types:
            typeset = self.data_types[datatype]
            for value in cargo_sort(datatype, typeset.values()):
                t += write_item(value, datatype)+"\n"
        t = t[:-1]
        return t

    def update_or_create(self, datatype, key, data):
        if datatype not in self.data_types:
            self.data_types[datatype] = {}
        if key not in self.data_types[datatype]:
            self.data_types[datatype][key] = {}
        self.data_types[datatype][key].update(data)

    def append(self, datatype, data):
        if datatype not in self.data_types:
            self.data_types[datatype] = {}
        unique = cargo_unique(datatype)
        if unique:
            for ob in self.data_types[datatype].values():
                flagged = True
                for k in unique:
                    if data.get(k, None)!=ob.get(k, None):
                        flagged = False
                        break
                if flagged:
                    return
        self.data_types[datatype][len(self.data_types[datatype])] = data

    def get_datas(self, datatype):
        return [self.data_types[datatype][key] for key in self.data_types[datatype]]

    def get_data(self, datatype):
        return self.get_datas(datatype)[0]
    
    def restrict_fields(self, fields=[], exclude_fields=[]):
        """ Modify the table to only include fields that match those in the list.
        Exclude fields explicitly skips fields, such as artist.
        Use '.' to separate namespace and field """
        for datatype in list(self.data_types.keys()):
            subset = self.data_types[datatype]
            for field in list(subset.keys()):
                # If no restricted fields were specified, we're trying to
                # include all fields.
                matching = not fields
                for match_field in fields:
                    if match_field in datatype+'.'+str(field):
                        matching = True
                        break
                # Exclude has to be specified and match to affect anything.
                exclude = False
                for match_field in exclude_fields:
                    if match_field in datatype+'.'+str(field):
                        exclude = True
                        break
                if exclude or not matching:
                    del self.data_types[datatype][field]
                    if not self.data_types[datatype]:
                        del self.data_types[datatype]
                        break

class MediawikiManager:
    def __init__(self, api):
        self.api = api
        self.skip = []
        self.check_before_write = True
    def write_page(self, title, text, reason):
        old_text = None
        page = self.api.page(title)
        if self.check_before_write:
            old_text = page.read()
        if old_text == text:
            return {"result": None, "msg": "No text was changed"}
        return {"result": page.edit(text, reason)}
    def read_page(self, title):
        page = self.api.page(title)
        return page.read()
        

if __name__ == "__main__":
    ct = CargoTable()
    ct.append("ErrataData", {'Version':'', 'Text':"this is the first text", 'Tag':"mm change"})
    ct.append("ErrataData", {'Version':'', 'Text':"this is the first text", 'Tag':"mm change"})
    ct.append("ErrataData", {'Version':"rulebook 1.2", 'Text':"this is a changed text", 'Tag':"mm change"})
    ct.append("ErrataData", {'Version':"rulebook 1.2", 'Text':"this is a changed text", 'Tag':"next set change"})
    ct.append("ErrataData", {'Version':"rulebook 1.5", 'Text':"this is a changed text again", 'Tag':"next set change"})
    print(ct.get_datas("ErrataData"))
    print(ct.output_text())
