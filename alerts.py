import passwords
import requests

def discord_alert(msg):
    r = requests.post(passwords.DISCORD_WEBHOOK, json={"content": msg})