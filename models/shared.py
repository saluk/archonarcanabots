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


def nice_set_name(num):
    return {
        "452": "Worlds Collide",
        "453": "Worlds Collide",  # Put the anomalies in the same set
        "341": "Call of the Archons",
        "435": "Age of Ascension",
        "479": "Mass Mutation"
    }[str(num)]

def short_set_name(num):
    return SETS[num]

def get_set_numbers():
    return SETS.keys()