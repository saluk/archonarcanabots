SETS = {452: "WC",
        453: "A",
        341: "CotA",
        435: "AoA",
        479: "MM",
        496: "DT",
        600: "WoE"}
SET_NAMES = {
    452: "Worlds Collide",
    453: "Anomaly",
    341: "Call of the Archons",
    435: "Age of Ascension",
    479: "Mass Mutation",
    496: "Dark Tidings",
    600: "Winds of Exchange"
}
# TODO turn set data into a row with 3 data points, maybe pull it out of the wiki database
NEW_SETS = []
SET_BY_NUMBER = {}
SET_ORDER = []
for numerical_set in sorted(SETS.keys()):
    setname = SETS[numerical_set]
    SET_ORDER.append(setname)
    SET_BY_NUMBER[setname] = numerical_set

def get_set_number_by_name(name):
    for set_num in SET_NAMES:
        if SET_NAMES[set_num] == name:
            return set_num
    return 100000

NEXT_SET = "Grim Reminders"

anomaly_meta = {
    (0,10): "Worlds Collide",
    (11,14): "Winds of Exchange"
}


def assigned_set_name(set_num, card_num):
    if str(set_num) == "453":
        icard_num = int(card_num[1:])
        for r in anomaly_meta:
            if icard_num >= r[0] and icard_num <= r[1]:
                return anomaly_meta[r]
        raise Exception(f"Could not find card number {card_num} in anomaly assignments {anomaly_meta}")
    return {
        "452": "Worlds Collide",
#        "453": "Worlds Collide",  # Put the anomalies in the same set
        "341": "Call of the Archons",
        "435": "Age of Ascension",
        "479": "Mass Mutation",
        "496": "Dark Tidings",
        "600": "Winds of Exchange"
    }.get(str(set_num), NEXT_SET)


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
