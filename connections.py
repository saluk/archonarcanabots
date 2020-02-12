import praw
import mw_api_client as mw
from passwords import *

def get_reddit():
    reddit = praw.Reddit(user_agent='%s (by /u/%s)'%(BOT_NAME, BOT_USER_NAME),
                     client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                     username=BOT_USER_NAME, password=USER_PASSWORD)
    reddit.keyforge = reddit.subreddit('KeyForgeGame')
    reddit.testing = reddit.subreddit('testingground4bots')
    return reddit

def get_wiki():
    wp = mw.Wiki("https://archonarcana.com/api.php", WIKI_BOT_NAME)
    wp.login(WIKI_BOT_LOGIN, WIKI_BOT_PASSWORD)
    return wp

