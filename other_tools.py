import carddb


def list_traits():
    begin = False
    traits = set()
    for i, card_name in enumerate(carddb.cards):
        card = carddb.get_latest(card_name)
        if not card["traits"]: continue
        for trait in re.findall("\w+", card["traits"]):
            traits.add(trait)
    for trait in traits:
        print(trait)


def find_card_not_a_card(wp):
    for page in wp.category("Card").categorymembers():
        page_title = page.title
        if page_title not in cards:
            print(page_title)


def set_protected(page):
    print("update permissions for page", page.title)
    result = page.protect({'edit': 'sysop', 'move': 'sysop'}, cascade=True)
    print(result)
    time.sleep(0.10)


def set_protections(wp):
    for category in ["Card", "Glossary", "Rules", "Tournament Rules"]:
        cat = wp.category(category)
        for page in cat.categorymembers():
            set_protected(page)