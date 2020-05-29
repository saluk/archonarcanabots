import re

category_markup = re.compile(r"\[\[Category:(\w| |-)+\]\]")
section_header = re.compile(r"^=+([\w ]+)=+", re.MULTILINE)
wikitable_row = re.compile(r"^\|-", re.MULTILINE)
wikitable = re.compile(r"\{\|(.|\n)*")


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
    return {"CardData": "Name",
            "SetData": "SetName"}.get(table_type, None)


def cargo_unique(datatype):
    return {"ErrataData": ("Version", "Text")}.get(datatype, None)


def cargo_sort(table_type, table):
    sort_function = {
        "SetData": lambda row: int(row["SetNumber"]) if row["SetNumber"] else 0,
        "AltArt": lambda row: (int(row["Year"]), row["File"])
    }.get(table_type, None)
    if sort_function:
        return sorted(table, key=sort_function)
    defkey = cargo_index(table_type)
    if defkey:
        return sorted(table, key=lambda row: row.get(defkey, ''))
    return table


class CargoTable:
    def __init__(self):
        self.data_types = {}

    def read_from_text(self, text):
        d = {}
        TYPE = 1
        ROW = 2
        mode = TYPE
        for line in text.split("\n"):
            if mode == TYPE:
                if line.startswith("{{"):
                    d["type"] = line[2:]
                    mode = ROW
                    continue
            elif mode == ROW:
                if line.startswith("|"):
                    left, right = line.split("=", 1)
                    d[left[1:]] = right
                elif line.startswith("}}"):
                    datatype = d["type"]
                    del d["type"]
                    if datatype not in self.data_types:
                        self.data_types[datatype] = {}
                    index_key = cargo_index(datatype)
                    if index_key:
                        key = d[index_key]
                    else:
                        key = len(self.data_types[datatype])
                    self.data_types[datatype][key] = d
                    d = {}
                    mode = TYPE

    def output_text(self):
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
                    print(data[k],ob[k])
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

ct = CargoTable()
ct.append("ErrataData", {'Version':'', 'Text':"this is the first text", 'Tag':"mm change"})
ct.append("ErrataData", {'Version':'', 'Text':"this is the first text", 'Tag':"mm change"})
ct.append("ErrataData", {'Version':"rulebook 1.2", 'Text':"this is a changed text", 'Tag':"mm change"})
ct.append("ErrataData", {'Version':"rulebook 1.2", 'Text':"this is a changed text", 'Tag':"next set change"})
ct.append("ErrataData", {'Version':"rulebook 1.5", 'Text':"this is a changed text again", 'Tag':"next set change"})
print(ct.get_datas("ErrataData"))
print(ct.output_text())