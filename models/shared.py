SETS = {452: "WC",
        453: "WC-A",
        341: "CotA",
        435: "AoA",
        479: "MM"}
SET_BY_NUMBER = {}
SET_ORDER = []
for numerical_set in sorted(SETS.keys()):
    setname = SETS[numerical_set]
    SET_ORDER.append(setname)
    SET_BY_NUMBER[setname] = numerical_set

NEXT_SET = "Dark Tidings"


def nice_set_name(num):
    return {
        "452": "Worlds Collide",
        "453": "Worlds Collide",  # Put the anomalies in the same set
        "341": "Call of the Archons",
        "435": "Age of Ascension",
        "479": "Mass Mutation"
    }.get(str(num), NEXT_SET)


def get_set_numbers():
    return SETS.keys()


def is_evil_twin(card_data):
    import re
    # TODO set to the right one when we know
    regex = re.compile("evil.*twin.*", re.IGNORECASE)
    if regex.findall(card_data["rarity"]): return True
    for key in card_data:
        if regex.findall(key) and card_data[key] in [True, "1", "True", "true", "yes"]:
            return True
    return False