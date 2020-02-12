import os
import re
import json
import connections
import pprint
import carddb
import time

post_db = {}
if os.path.exists("reddit_post_index.json"):
    with open("reddit_post_index.json") as f:
        post_db = json.loads(f.read())

def forever_try_reply(content, text):
    sleep = 1
    while 1:
        try:
            content.reply(text)
            break
        except:
            sleep*2
            time.sleep(sleep)

def can_respond(reddit_id):
    if reddit_id not in post_db:
        return True
    return False
def record_response(content, text, reddit_id):
    forever_try_reply(content, text)
    post_db[reddit_id] = True
    with open("reddit_post_index.json", "w") as f:
        f.write(json.dumps(post_db))

reddit = connections.get_reddit()
wp = connections.get_wiki()

card_searches = {}
cat_searches = {}

def is_good_category(card_page):
    for c in card_page.categories():
        if c.title in ["Category:Card", "Category:Rules",
                        "Category:Glossary", "Category:Tournament Rules"]:
            return True

def lookup_card(name):
    sname = carddb.fuzzyfind(name) or name
    if sname not in card_searches:
        found = []
        page = wp.page(sname)
        if is_good_category(page):
            found.append(page)
        search_page = wp.search(sname, srwhat="text", srredirect=True)
        print(list(search_page))
        if not found:
            card_searches[sname] = None
            return None
        else:
            p = found[0]
            card_searches[sname] = {"url": p.info()["canonicalurl"], 
                                    "title": p.info()["displaytitle"]}
    if card_searches[sname]:
        return card_searches[sname]

def get_cards(text):
    if not text or text=="[deleted]":
        return []
    for match in re.findall("\[.*?\]", text):
        card_name = match[1:-1]
        url = lookup_card(card_name)
        if url:
            yield url
        else:
            print("FAIL",card_name)

def do_reply(content, cards):
    if not cards:
        return
    t = "Here are some links courtesy of Archon Arcana:  \n"
    for c in cards:
        t += '* [%(title)s](%(url)s)  \n' % c
    if can_respond(content.id):
        print(t)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        record_response(content, t, content.id)


def reply_submission(submission):
    #if submission.url != "https://www.reddit.com/r/KeyforgeGame/comments/ez9e5t/what_are_combos_to_look_out_for/":
    #    return
    print("SUBMISSION:", submission.url)
    #print("selftext",block.selftext)
    #pprint.pprint(dir(block))
    for comment in submission.comments:
        reply_comment(comment)
    do_reply(submission, list(get_cards(submission.selftext_html)))

def reply_comment(comment):
    #print("COMMENT:", comment.body)
    print("COMMENT:", comment.id)
    #pprint.pprint(dir(comment))
    for comment in getattr(comment, "comments", []):
        reply_comment(comment)
    do_reply(comment, list(get_cards(comment.body_html)))
    
submission = reddit.submission("f2htrb")
pprint.pprint(submission)
print(dir(submission))
print(submission.comments[0].body)
print(submission.selftext)
#reply_submission(submission)
#crash

def next_comment_or_submission(subreddit):
    submissions = subreddit.stream.submissions(pause_after=5)
    comments = subreddit.stream.comments(pause_after=5)
    while 1:
        stop_after = 5
        for sub in submissions:
            if not sub:
                break
            print("replying to submission")
            yield "submission", sub
            stop_after -= 1
            if stop_after<=0:
                break
        stop_after = 5
        for comment in comments:
            if not comment:
                break
            print("replying to comment")
            yield "comment", comment
            stop_after -= 1
            if stop_after<=0:
                break
        time.sleep(5)

for content_type,content in next_comment_or_submission(reddit.keyforge):
    print(content_type)
    if content_type=="comment":
        reply_comment(content)
    elif content_type=="submission":
        reply_submission(content)
    else:
        raise Exception("Bad content_type:"+content_type)
