import wikitextparser as wtp
from wikibase import CargoTable

class Parser:
    def __init__(self):
        self.sections = {}
        self.rows = []
    def parse_country(self, section):
        self.sections[section.level] = section.title and section.title.strip()
        level = section.level+1
        while level in self.sections:
            del self.sections[level]
            level += 1
        if not section.contents:
            return
        if "{|" not in section.contents.split("==",1)[0]:
            return
        path = [self.sections[key] for key in sorted(list(self.sections.keys()))]
        self.path = path
        return [self.parse_table(t) for t in section.tables]
    def parse_table(self, table):
        data = table.data(span=False)[:]
        tags = []
        while data:
            row = data.pop(0)
            if len(row)==1:
                tags.append(row[0])
            else:
                data.insert(0, row)
                break
        header = data.pop(0)
        for row in data:
            self.add_row(tags, header, row)
    def add_row(self, tags, header, row):
        d = {
        }
        d["Continent"] = self.path[1].replace(",", ";")
        d["Country"] = self.path[2]
        if len(self.path) > 3:
            d["StateProvince"] = self.path[3]
        if tags:
            d["Region"] = tags[0]
        columns = {"Name": "OrgName", "Type": "OrgType",
            "City":"OrgCity", "Notes":"OrgNotes"}
        for i, col in enumerate(header):
            d[columns[col]] = row[i]
        name = d["OrgName"]
        p = wtp.parse(name)
        links = p.wikilinks + p.external_links
        if links:
            name = links[0].text.strip()
        ct = CargoTable("Local:"+name)
        ct.update_or_create("LocalScene", name, d)
        self.rows.append(ct)

parser = Parser()

def parse_tables(t):
    parsed = wtp.parse(t)
    sections = parsed.sections
    [parser.parse_country(section) for section in sections]
    for row in parser.rows:
        s = row.output_text()
    return parser.rows

def write(mwm):
    text = mwm.read_page("Local_Groups_and_Shops")
    rows = parse_tables(text)
    for row in rows:
        print(mwm.write_page(row.page_name, row.output_text(), "Building local scene tables"))