from util import cargo_query

class SetData:
    def __init__(self):
        self.sets = {}
        self.anomaly_sets = {}
    def get_set_data(self):
        search = {
            "tables": 'SetInfo',
            "fields": "SetNumber, ShortName, SetName, ReleaseYear, ReleaseMonth, IsMain, IsSpoiler, IsAdventure, AnomalyRange"
        }
        for result in cargo_query(search)['cargoquery']:
            kfset = result['title']
            self.sets[kfset["SetNumber"]] = kfset
            for field in kfset:
                if kfset[field]:
                    kfset[field] = kfset[field].strip()
            for field in ["ReleaseYear", "ReleaseMonth"]:
                if kfset[field]:
                    kfset[field] = int(kfset[field])
            for field in ["IsMain", "IsSpoiler", "IsAdventure"]:
                if kfset[field]:
                    kfset[field] = bool(int(kfset[field]))
            if kfset.get("AnomalyRange", None):
                vs = kfset["AnomalyRange"].split("-",1)
                if len(vs)==0:
                    self.anomaly_sets[int(vs[0])] = kfset
                else:
                    for i in range(int(vs[0]), int(vs[1])+1):
                        self.anomaly_sets[i] = kfset
    def find_set(self, query):
        # TODO faster find if query is the SetNumber
        for kfset in self.sets.values():
            if str(query).lower() in [
                    n.lower() for n in [
                        kfset["SetName"], kfset["ShortName"]
                    ]] or str(query).lower() == str(kfset["SetNumber"]).lower():
                return kfset
    def assigned_set_name(self, set_query, card_num=None):
        if str(set_query) == "453":
            icard_num = int(card_num[1:])
            return self.anomaly_sets[icard_num]["SetName"]
        set_info = self.find_set(set_query)
        if not set_info:
            print(
                '\n*** Set code %s not found. Check %s.' % (
                    str(set_query),
                    'https://archonarcana.com/Special:CargoQuery?title=Special%3ACargoQuery&tables=SetInfo'
                )
            )
        set_num = set_info["SetNumber"]
        return self.sets[str(set_num)]["SetName"]
    def is_spoiler(self, query):
        return self.find_set(query)["IsSpoiler"]
    def sort_order(self, set_query):
        number = self.find_set(set_query)["SetNumber"]
        # Strip letters from number
        number = "".join([x for x in str(number) if str(x).isdigit()])
        return int(number)

set_data = SetData()
set_data.get_set_data()

SETS = {452: "WC",
        453: "A",
        341: "CotA",
        435: "AoA",
        479: "MM",
        496: "DT",
        600: "WoE",
        601: "U2023",
        609: "VM2023",
        700: "GR",
        722: "MN2024",
        737: "VM2024",
        800: "ÆS",
        855: "ToC",
        874: "MoMu",
        886: "PV",
        892: "MCW",
        907: "Disc",
        918: "CC",
        939: "VM25",
        }
SET_NAMES = {
    452: "Worlds Collide",
    453: "Anomaly",
    341: "Call of the Archons",
    435: "Age of Ascension",
    479: "Mass Mutation",
    496: "Dark Tidings",
    600: "Winds of Exchange",
    601: "Unchained 2023",
    609: "Vault Masters 2023",
    700: "Grim Reminders",
    722: "Menagerie 2024",
    737: "Vault Masters 2024",
    800: "Æmber Skies",
    855: "Tokens of Change",
    874: "More Mutation",
    886: "Prophetic Visions",
    892: "Martian Civil War",
    907: "Discovery",
    918: "Crucible Clash",
    939: "Vault Masters 2025",
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

NEXT_SET = "Draconian Measures"
SPOILER_SETS = ["Draconian Measures"]


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
