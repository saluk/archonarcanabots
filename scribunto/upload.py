import os
import connections
wp = connections.get_wiki()
import json

def upload_lua_file(filename, test=False):
    with open("scribunto/"+filename) as f:
        txt = f.read()
        wpname = txt.split('\n')[0].rsplit('--', 1)[1].strip()
        print(wpname)
        if not test:
            page = wp.page(wpname)
            print(page.edit(txt, wpname, "file updated"))

def upload(test=False):
    for filename in os.listdir('scribunto'):
        if filename.endswith('.py'):
            continue
        if os.path.isdir('scribunto/'+filename):
            continue
        upload_lua_file(filename, test)
