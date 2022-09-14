import wikitextparser as wtp
from wikibase import CargoTable, update_page
import json
import requests
import re
from util import cargo_query
from datetime import date
import alerts

def read_spreadsheet(sheet_url):
    r = requests.get(sheet_url)
    r.encoding = 'utf8'
    rows = [line.split('\t') for line in re.split("\r\n|\n|\r", r.text)]
    print(rows[0])
    print(rows[1])
    print(rows[2])
    print(rows[3:])
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
        self.sheet_url = sheet_url
        self.rows = read_spreadsheet(sheet_url)
        self.title = None
        self.title_key = None
        self.make_page = False
        self.duplicates = [None, None, None]
        self.read_meta()
        self.filter_rows()
        self.cargotables = {}
    @property
    def edit_url(self):
        return self.sheet_url.rsplit('/', 1)[0]+'/edit?usp=sharing'
    def read_meta(self):
        if self.rows[0][0]!='meta':
            raise Exception("No meta defined")
        meta, self.rows = self.rows[0], self.rows[1:]
        for m in meta:
            if ":" in m:
                k,v = m.split(":", 1)
                if k == 'duplicates':
                    v = v[1:-1].split(' ')
                setattr(self,k,v)
    def filter_rows(self):
        self.rows = [x for x in self.rows if [y for y in x if y.strip()]]
    def merge_single(self):
        current = CargoTable()
        keys, rows = self.rows[0], self.rows[1:]
        keys = [col for col in keys if col.strip()]
        for rowi, row in enumerate(rows):
            ob = {}
            for i, key in enumerate(keys):
                ob[key] = row[i]
            current.update_or_create(self.table, rowi, ob)
        self.cargotables[self.title] = current
    def merge_multiple(self):
        tables, keys, rows = self.rows[0], self.rows[1], self.rows[2:]
        print(keys, tables)
        title = None
        for rowi, row in enumerate(rows):
            obs = {}
            can_publish = True
            publish_date = None
            for i, key in enumerate(keys):
                table = tables[i]
                if not table.strip() or not key.strip():
                    continue
                if key == "PublishDate":
                    if row[i].strip():
                        publish_date = date.fromisoformat(row[i].strip())
                        if publish_date > date.today():
                            can_publish = False
                    continue
                if table not in obs:
                    obs[table] = {}
                obs[table][key] = row[i]
                if self.title_key == key:
                    title = row[i]
            if not title:
                raise Exception(f"No title found for {self.title_key}")
            if not can_publish:
                alerts.discord_alert(f"Page {title} won't be published until {publish_date}")
                continue
            current = CargoTable()
            for table in obs:
                copies = [obs[table]]
                if table == self.duplicates[0]:
                    copies = []
                    for segment in obs[table][self.duplicates[1]].split(self.duplicates[2]):
                        r = {}
                        r.update(obs[table])
                        r[self.duplicates[1]] = segment.strip()
                        copies.append(r)
                for i,copy in enumerate(copies):
                    current.update_or_create(table, rowi+i, copy)
            self.cargotables[title] = current
        for title in self.cargotables:
            print(self.cargotables[title].data_types)
    def to_page(self, wp, pause):
        self.merge_single()
        cargotable = self.cargotables[self.title]
        if update_page(
            self.title,
            wp.page(self.title),
            f"<noinclude>This data was populated from {self.edit_url} - edits may later be overwritten.</noinclude>\n" + cargotable.output_text(),
            f"updating {self.title} from spreadsheet",
            "",
            pause=pause,
            read=True
        ):
            alerts.discord_alert(f"Cargo table {self.title} updated from spreadsheet {self.edit_url}")
            return True
    def to_pages(self, wp, pause):
        if not self.title and not self.title_key:
            raise Exception("Spreadsheet meta must include a title or a title_key")
        if self.title and not self.title_key:
            return self.to_page(wp, pause)
        self.merge_multiple()
        changes = []
        for title, cargotable in self.cargotables.items():
            data_change = update_page(
                self.title_prefix+":"+title,
                wp.page(self.title_prefix+":"+title),
                f"<noinclude>This data was populated from {self.edit_url} - edits may later be overwritten.</noinclude>\n" + cargotable.output_text(),
                f"updating {title} from spreadsheet",
                "",
                pause=pause,
                read=True
            )
            if data_change:
                alerts.discord_alert(f"Cargo table {title} updated from spreadsheet {self.edit_url}")
            changes.append(data_change)
            if self.make_page:
                change = update_page(
                    title,
                    wp.page(title),
                    self.make_page % {"title": title},
                    f"updating {title} from spreadsheet with make page",
                    "",
                    pause=pause,
                    read=True
                )
                if change:
                    alerts.discord_alert(f"Page {title} updated from spreadsheet {self.edit_url}")
                changes.append(change)
                if data_change:
                    wp.page(title).purge()
        return changes
                

def merge(wp, sheet_name=None, pause=True):
    with open('data/spreadsheets.json') as f:
        spreadsheets = json.loads(f.read())['google_links']
    changed = []
    for sheet, url in spreadsheets.items():
        if sheet_name and not sheet == sheet_name:
            continue
        if sheet == "translated_terms":
            success = LocaleMerger(url).to_pages(wp, pause)
        else:
            success = Merger(url).to_pages(wp, pause)
        if success:
            changed.append(sheet)
    return changed

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