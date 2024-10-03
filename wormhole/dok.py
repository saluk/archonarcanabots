import requests

my_decks_ep = "https://decksofkeyforge.com/public-api/v1/my-decks"
api_key = "de34e2c4-608c-4e98-a51b-4077c3548dc9"

def get_decks(api_key):
	r = requests.get(my_decks_ep, headers={"Api-Key":api_key})
	return r.json()
