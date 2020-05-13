import os
import connections
wp = connections.get_wiki()


def upload():
    for filename in os.listdir("javascript"):
        if not filename.endswith(".js"):
            continue
        if filename.startswith("."):
            continue
        wpname = "MediaWiki:" + filename
        print(wpname)
        page = wp.page(wpname)
        with open("javascript/"+filename) as f:
            print(page.edit(f.read(), "javascript updated"))
