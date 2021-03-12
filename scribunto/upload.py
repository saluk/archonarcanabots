import os
import connections
wp = connections.get_wiki()
import re

def upload_lua_file(filename, test=False, mode='dev'):
    with open("scribunto/"+filename) as f:
        txt = f.read()
        wpname = txt.split('\n')[0].rsplit('--', 1)[1].strip()
        if txt.find("--canstage")>=0:
            if mode != "prod":
                wpname += '2'
                txt = re.sub('require\(\'(.*?)\'\)', r"require('\g<1>2')", txt)
                print(re.findall('require.*?\)', txt))
        print(wpname)
        if not test:
            page = wp.page(wpname)
            print(page.edit(txt, wpname, "file updated"))

def upload(test=False, mode='dev'):
    for filename in os.listdir('scribunto'):
        if filename.endswith('.py'):
            continue
        if os.path.isdir('scribunto/'+filename):
            continue
        upload_lua_file(filename, test, mode)
