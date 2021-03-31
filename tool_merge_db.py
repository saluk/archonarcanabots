import wikitextparser as wtp
from wikibase import CargoTable, update_page
import json
import requests
import re
from util import cargo_query

def read_spreadsheet(sheet_url):
    r = requests.get(sheet_url)
    r.encoding = 'utf8'
    rows = [line.split('\t') for line in re.split("\r\n|\n|\r", r.text)]
    print(rows[0])
    print(rows[1])
    print(rows[2])
    print(rows[3])
    print(rows[4])
    return rows

def get_locale_spreadsheet(sheet_url):
    locale_spreadsheet={}
    rows = read_spreadsheet(sheet_url)
    locales = rows[0][2:]
    for cols in rows[1:]:
        if not cols[0]:
            continue
        type,englishtext = cols[:2]
        for i,locale in enumerate(locales):
            translatedtext = cols[2:][i].strip()
            if not translatedtext:
                continue
            key = (englishtext,locale,type)
            key = englishtext+"..."+locale+"..."+type
            locale_spreadsheet[key] = translatedtext
    #print(locale_spreadsheet)
    assert locale_spreadsheet.get('note set availability...ru-ru...disclaimer')
    #print(locale_spreadsheet['note set availability...ru-ru...disclaimer'])
    #print([x for x in locale_spreadsheet.keys() if x.find('it-it')])
    #print([x for x in locale_spreadsheet.keys() if x.find('th-th')])
    return locale_spreadsheet

class LocaleMerger:
    def __init__(self, sheet_url):
        self.spreadsheet = get_locale_spreadsheet(sheet_url)
        self.cargotable = CargoTable()
        self.title = "CardLocaleData:TranslationTable"
    def parse_cargo(self, page):
        self.cargotable.read_from_text(page.read())
        print(self.cargotable.get_datas("TranslationTable"))
    def merge(self):
        for k,v in self.spreadsheet.items():
            (englishtext, locale, type) = k.split("...")
            translatedtext = v
            self.cargotable.update_or_create("TranslationTable", (englishtext, locale), {
                "Type":type, 
                "TranslatedText": translatedtext,
                "EnglishText": englishtext,
                "Locale": locale
            })
    def to_page(self, wp):
        page = wp.page(self.title)
        self.parse_cargo(page)
        self.merge()
        update_page(
            self.title,
            page,
            self.cargotable.output_text(),
            f"updating {self.title} from spreadsheet",
            "",
            pause=True,
            read=True
        )

class Merger:
    def __init__(self, sheet_url):
        self.rows = read_spreadsheet(sheet_url)
        self.title = None
        self.read_meta()
        self.filter_rows()
        self.cargotable = CargoTable()
    def read_meta(self):
        if self.rows[0][0]!='meta':
            raise Exception("No meta defined")
        meta, self.rows = self.rows[0], self.rows[1:]
        self.title = meta[1]
        self.table = meta[2]
        self.row_model = meta[3]
        self.col_model = meta[4]
    def filter_rows(self):
        self.rows = [x for x in self.rows if [y for y in x if y.strip()]]
    def merge_object_keys(self):
        keys, rows = self.rows[0], self.rows[1:]
        keys = [col for col in keys if col.strip()]
        for rowi, row in enumerate(rows):
            ob = {}
            for i, key in enumerate(keys):
                ob[key] = row[i]
            self.cargotable.update_or_create(self.table, rowi, ob)
    def merge(self):
        if self.row_model=="row:OBJECT" and self.col_model == "col:KEY":
            self.merge_object_keys()
        else:
            raise Exception("Unknown row/column format")
    def to_page(self, wp):
        page = wp.page(self.title)
        #self.parse_cargo(page)
        self.merge()
        update_page(
            self.title,
            page,
            self.cargotable.output_text(),
            f"updating {self.title} from spreadsheet",
            "",
            pause=True,
            read=True
        )

def merge(wp):
    with open('data/spreadsheets.json') as f:
        spreadsheets = json.loads(f.read())['google_links']
    for sheet, url in spreadsheets.items():
        if sheet == "translated_terms":
            LocaleMerger(url).to_page(wp)
        else:
            Merger(url).to_page(wp)

def access_table(table, fields):
    search = {
        "tables": table,
        "fields": ','.join(fields)
    }
    return [result['title'] for result in cargo_query(search)['cargoquery']]
            
def export(table):
    with open('data/spreadsheets.json') as f:
        spreadsheets = json.loads(f.read())
    fields = spreadsheets.get('table_fields').get(table)
    with open(f'data/table_{table}.csv','w') as f:
        f.write('\t'.join(fields)+'\n')
        for row in access_table(table, fields):
            print(row)
            field_results = []
            for field in fields:
                field_results.append(row[field].replace('\n','\\n'))
            f.write('\t'.join(field_results)+'\n')