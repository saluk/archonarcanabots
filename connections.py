import praw
import mw_api_client as mw
passwords = None
try:
    import passwords
except:
    pass


def get_reddit():
    reddit = praw.Reddit(user_agent='%s (by /u/%s)' % (
                            passwords.REDDIT_BOT_NAME,
                            passwords.REDDIT_BOT_USER_NAME),
                         client_id=passwords.REDDIT_CLIENT_ID,
                         client_secret=passwords.REDDIT_CLIENT_SECRET,
                         username=passwords.REDDIT_BOT_USER_NAME,
                         password=passwords.REDDIT_USER_PASSWORD)
    reddit.keyforge = reddit.subreddit('KeyForgeGame')
    reddit.testing = reddit.subreddit('testingground4bots')
    return reddit


def get_wiki():
    wp = mw.Wiki("https://archonarcana.com/api.php", passwords.WIKI_BOT_NAME)
    wp.login(passwords.WIKI_BOT_LOGIN, passwords.WIKI_BOT_PASSWORD)
    return wp

