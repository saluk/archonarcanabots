import sys, os
sys.path.insert(0, os.path.abspath(__file__).rsplit("/", 1)[0]+'/../..')
import models.mv_model as mv

f = open("data/rescrape_decks.csv")
pages = f.read().split("\n")
f.close()

scraped = set()

session = mv.Session()
existing_tasks = session.query(mv.ScrapePageTask).all()
for task in existing_tasks:
    scraped.add(str(task.page))
session.close()

unique_pages = []
for p in pages:
    if p not in scraped and p:
        scraped.add(p)
        unique_pages.append(p)

session = mv.Session()
for page_number in unique_pages:
    task = mv.ScrapePageTask(page=int(page_number), per_page=24)
    session.add(task)
session.commit()