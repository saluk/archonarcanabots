import wikitextparser as wtp
from wikibase import CargoTable, update_page

spreadsheet = {}
with open("data/Archon Arcana Translations - terms.tsv") as f:
    rows = f.read().split("\n")
    locales = rows[0].split("\t")[2:]
    print(locales)
    for row in rows[1:]:
        cols = row.split("\t")
        if not cols[0]:
            continue
        type,englishtext = cols[:2]
        for i,locale in enumerate(locales):
            translatedtext = cols[2:][i].strip()
            if not translatedtext:
                continue
            key = (englishtext,locale,type)
            spreadsheet[key] = translatedtext
print(spreadsheet)
print([x for x in spreadsheet.keys() if x[1]=='it-it'])
print([x for x in spreadsheet.keys() if x[1]=='th-th'])


class Merger:
    def __init__(self):
        self.spreadsheet = spreadsheet
        self.cargotable = CargoTable()
    def parse_cargo(self, page):
        self.cargotable.read_from_text(page.read())
        print(self.cargotable.get_datas("TranslationTable"))
    def merge_up(self):
        for k,v in self.spreadsheet.items():
            (englishtext, locale, type) = k
            translatedtext = v
            self.cargotable.update_or_create("TranslationTable", (englishtext, locale), {
                "Type":type, 
                "TranslatedText": translatedtext,
                "EnglishText": englishtext,
                "Locale": locale
            })
    def merge(self, direction):
        getattr(self, "merge_"+direction)()
        print(self.cargotable.get_datas("TranslationTable"))

merger = Merger()

def merge(wp, direction):
    title = "CardLocaleData:TranslationTable"
    page = wp.page(title)
    merger.parse_cargo(page)
    merger.merge(direction)
    update_page(title, page, merger.cargotable.output_text(), "updating translationtable from spreadsheet", "", pause=True, read=True)
