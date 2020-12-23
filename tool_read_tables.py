import wikitextparser as wtp
from wikibase import CargoTable

class Parser:
    def __init__(self):
        self.sections = {}
        self.rows = []
    def parse_country(self, section):
        self.sections[section.level] = section.title and section.title.strip()
        level = section.level+1
        while level in self.sections:
            del self.sections[level]
            level += 1
        if not section.contents:
            return
        if "{|" not in section.contents.split("==",1)[0]:
            return
        path = [self.sections[key] for key in sorted(list(self.sections.keys()))]
        self.path = path
        return [self.parse_table(t) for t in section.tables]
    def parse_table(self, table):
        data = table.data(span=False)[:]
        tags = []
        while data:
            row = data.pop(0)
            if len(row)==1:
                tags.append(row[0])
            else:
                data.insert(0, row)
                break
        header = data.pop(0)
        for row in data:
            self.add_row(tags, header, row)
    def add_row(self, tags, header, row):
        d = {
        }
        d["Continent"] = self.path[1]
        d["Country"] = self.path[2]
        if len(self.path) > 3:
            d["StateProvince"] = self.path[3]
        if tags:
            d["Region"] = tags[0]
        columns = {"Name": "OrgName", "Type": "OrgType",
            "City":"OrgCity", "Notes":"OrgNotes"}
        for i, col in enumerate(header):
            d[columns[col]] = row[i]
        name = d["OrgName"]
        p = wtp.parse(name)
        links = p.wikilinks + p.external_links
        if links:
            name = links[0].text.strip()
        ct = CargoTable("Local:"+name)
        ct.update_or_create("LocalScene", name, d)
        self.rows.append(ct)

parser = Parser()

def parse_tables(t):
    parsed = wtp.parse(t)
    sections = parsed.sections
    [parser.parse_country(section) for section in sections]
    for row in parser.rows:
        s = row.output_text()
    return parser.rows

text = """
Below is a list of local groups and shops that are known to support KeyForge Organized Play.

Archon Arcana does not take any responsibility for the accuracy of this list, and strongly suggests reaching out to the organization or venue directly for details about their events. Have something to add to this list? [[:Special:CreateAccount|Create an account]] and send us a note in our [https://discord.com/invite/JQC99Fm Discord], you can also send the information to us in an [mailto:localplay@archonarcana.com email]. 

==Africa==
==Asia==
==Australia==
==Europe==

=== France ===
{| class="wikitable sortable"
!Name
!Type
!City
!Notes
|-
|KeyForge France
|Group
|
|[https://discord.gg/npZHjWtYVR Discord]
|}
===Portugal===
{| class="wikitable sortable"
|-
! Name||Type||City||Notes
|-
| [https://www.ajogar.com A Jogar é que a gente se entende]|| Cafe || Vila do Conde ||Chainbound (Monday, Thursday), Online tournaments (Tuesday), Longer Tournaments (Saturdays)

|}

=== Spain ===
{| class="wikitable sortable"
!Name
!Type
!City
!Notes
|-
|Comunidad KeyForge España
|Group
|
|[https://twitter.com/ComunidadKFE Twitter], [https://www.instagram.com/comunidadkfe/ Instagram], [https://www.facebook.com/Comunidad-Keyforge-Espa%C3%B1a-105374934794958 Facebook]
|}

===United Kingdom===
The main community group is the [https://www.facebook.com/groups/KeyForgeUK KeyForge UK] group on Facebook. All in-person KeyForge events are currently on hold due to [https://www.gov.uk/coronavirus COVID-19].
{| class="wikitable sortable"
! colspan="4" |East Anglia
|-
!Name
!Type
!City
!Notes
|-
|Stevenage KeyForge
|Group
|Stevenage
|[https://www.facebook.com/groups/432312594304713/?hc_location=ufi Facebook]
|-
|Calamity Comics Hatfield
|Store
|[https://www.google.com/maps/place/Calamity+Comics/@51.7577644,-0.2346444,13.88z/data=!4m5!3m4!1s0x48763c833c597f7b:0xc2c69672096d4705!8m2!3d51.764269!4d-0.226408 Hatfield]
|[https://www.facebook.com/Calamity-Comics-Hatfield-1754376134806335/ Facebook]
|-
|[https://www.theboardgamehut.co.uk/store-location/ The Board Game Hut]
|Store
|[https://www.google.com/maps/place/The+Board+Game+Hut/@51.5400478,0.6834692,14.83z/data=!4m5!3m4!1s0x47d8d9eb2fe0cc4d:0x38deeef8ece3d8a2!8m2!3d51.5389975!4d0.6933521 Westcliff-on-Sea]
|[https://discord.gg/CyB24sW Discord]
|}
{| class="wikitable sortable"
! colspan="4" |East Midlands
|-
!Name
!Type
!City
!Notes
|-
|Geeks Headquarters
|Store
|[https://www.google.com/maps/place/Geeks+Headquarters/@53.2368642,-1.4321747,17z/data=!3m1!4b1!4m5!3m4!1s0x4879853a0754afc9:0x8478384ccf048be3!8m2!3d53.236861!4d-1.429986 Chesterfield]
|[https://www.facebook.com/geeksheadquarters/ Facebook], [https://www.facebook.com/groups/362639347616519/ GHQ Keyforge Facebook]
|-
|[http://www.thegamesstore.com/ The Games Store]
|Store
|[https://www.google.com/maps/place/Comic+Culture+%26+The+Games+Store/@53.2283411,-0.540615,15.96z/data=!4m8!1m2!2m1!1sthe+games+store+lincoln!3m4!1s0x48785b24cc4df3f9:0x3f76509baaac7365!8m2!3d53.2294067!4d-0.5391847 Lincoln]
|
|-
|[https://dicecupcafe.co.uk/ The Dice Cup]
|Store
|Nottingham
|Chainbound on Wednesday evenings. Food and drink served.  [https://www.facebook.com/groups/KeyforgeDiceCup/?hc_location=ufi Keyforge @ The Dice Cup Facebook]
|-
|[https://www.boardsandswords.co.uk/pages/visit-us Boards & Swords]
|Store
|Derby
|
|-
|[https://sanctuarygamingcentre.co.uk/how-to-find-us/ Sanctuary Gaming Centre]
|Store
|Sutton-in-Ashfield
|
|}

{| class="wikitable sortable"
! colspan="4" |Greater London
|-
!Name
!Type
!City
!Notes
|-
|London KeyForge
|Group
|
|[https://www.facebook.com/groups/1781656971960683/ Facebook]
|-
|[https://www.theludoquist.com/ The Ludoquist]
|Store
|Croydon
|Food and drink served. [https://discord.gg/Beu2xrg Discord]
|-
|[https://www.rulezero.co.uk/ Rule Zero Games Bar]
|Store
|Stratford
|Chainbound on Saturdays. [https://discord.gg/utCBXnKjta Discord]
|-
|[https://www.darksphere.co.uk/shop.php Dark Sphere Waterloo]
|Store
|Waterloo
|
|-
|[https://leisuregames.com/ Leisure Games]
|Store
|Finchley
|
|-
|[https://www.d20cafe.co.uk/ d20 Board Game Cafe]
|Store
|Watford
|
|-
|[https://www.eclecticgames.co.uk/ Eclectic Games]
|Store
|Reading
|
|}
{| class="wikitable sortable"
! colspan="4" |North East
|-
!Name
!Type
!City
!Notes
|-
|[https://www.beaniegames.co.uk/ Beanie Games]
|Store
|Stockton-on-Tees
|
|-
|[https://www.midlamminiatures.co.uk/ Midlam Miniatures]
|Store
|Gateshead
|
|-
|[https://gamersathart.co.uk/ Gamers-at-Hart Cafe]
|Store
|Hartlepool
|[https://www.facebook.com/TeaAtHart Facebook]
|}
{| class="wikitable sortable"
! colspan="4" |North West
|-
!Name
!Type
!City
!Notes
|-
|[https://justplaygames.uk/ JustPlay]
|Store
|Liverpool
|[https://www.facebook.com/groups/358486381585644/ JustPlay: Keyforge Facebook]
|-
|[https://www.fanboy3.co.uk/ Fan Boy Three]
|Store
|Manchester
|Chainbound on Friday evenings. [https://www.facebook.com/groups/2012442305509605/?hc_location=group Fan Boy Three Keyforge Facebook], [https://discord.gg/fvX6g2g Discord]
|-
|Manchester Keyforgers
|Group
|Manchester
|[https://www.facebook.com/groups/2261920537456081/ Facebook]
|-
|[https://bastion-gaming.org.uk/home Bastion Gaming Church]
|Store
|Oldham
|[https://www.facebook.com/bastiongamingchurch/ Facebook], [https://twitter.com/gamingbastion Twitter], [https://discord.gg/W2UKre2G5s Discord]
|-
|[https://harlequins-games.co.uk/ Harlequins Gaming Store]
|Store
|Preston
|Chainbound on Sundays.
|-
|Preston Keyforgers
|Group
|Preston
|[https://www.facebook.com/groups/2441414512536794/ Facebook]
|}
{| class="wikitable sortable"
! colspan="4" |Scotland
|-
!Name
!Type
!City
!Notes
|-
|Keyforge Scotland
|Group
|
|[https://www.facebook.com/groups/273837473414568 Facebook]
|-
|[https://elleriumgames.co.uk/ Ellerium Games]
|Store
|Inverness
|[https://www.facebook.com/Elleriumgames/ Facebook]
|-
|[http://www.reddicegames.com/ Red Dice Games]
|Store
|Edinburgh
|[https://www.facebook.com/reddicegames/ Facebook]
|}
{| class="wikitable sortable"
! colspan="4" |South East
|-
!Name
!Type
!City
!Notes
|-
|[https://www.thegamingden.co.uk/ The Gaming Den]
|Store
|Basingstoke
|
|-
|[https://www.dicesaloon.com/pages Dice Saloon]
|Store
|Brighton
|Chainbound on Tuesday evenings.
|-
|Brighton Crucible
|Group
|Brighton
|[https://www.facebook.com/groups/713656949000766/?hc_location=ufi Facebook]
|-
|[https://diceportsmouth.com/ Dice Portsmouth]
|Store
|Portsmouth
|Chainbound on Wednesday evenings.
|-
|[https://www.afistfulofdice.co.uk/ A Fistful of Dice]
|Store
|Portsmouth
|Chainbound on Friday evenings.
|-
|[https://www.boardinthecity.co.uk/ Board in the City CIC]
|Store
|Southampton
|Chainbound on Monday evenings.
|-
|[http://teamexalted.com/ Team Exalted]
|Group
|
|[https://www.facebook.com/teamexaltedKf/ Facebook]
|}
{| class="wikitable sortable"
! colspan="4" |South West
|-
!Name
!Type
!City
!Notes
|-
|[https://excelsiorgamesandcomics.co.uk/ Excelsior! Comics]
|Store
|Bristol
|Chainbound on alternating Thursday evenings.
|-
|KeyForge Bristol
|Group
|Bristol
|[https://www.facebook.com/groups/keyforgebristol/ Facebook]
|-
|[https://osiris.games/ Osiris Games]
|Store
|Cheltenham
|
|}
{| class="wikitable sortable"
! colspan="4" |Wales
|-
!Name
!Type
!City
!Notes
|-
|[https://www.firestormgames.co.uk/location-opening-times Firestorm Games]
|Store
|Cardiff
|[https://www.facebook.com/groups/SWGCLCG FFG Games at Firestorm Games Facebook]
|-
|[https://www.thegamersemporium.co.uk/ The Gamers' Emporium]
|Store
|Swansea
|
|-
|South Wales Sneklifters
|Group
|
|[https://www.facebook.com/SouthWalesSneklifters/?hc_location=ufi Facebook]
|}
{| class="wikitable sortable"
! colspan="4" |West Midlands
|-
!Name
!Type
!City
!Notes
|-
|[https://www.chanceandcounters.com/birmingham/ Chance & Counters Birmingham]
|Store
|Birmingham
|Food and drink served.
|-
|Birmingham KeyForge
|Group
|Birmingham
|[https://www.facebook.com/groups/664533467418178/ Facebook]
|-
|[https://www.spiritgames.co.uk/ Spirit Games]
|Store
|Burton on Trent
|
|}
{| class="wikitable sortable"
! colspan="4" |Yorkshire & The Humber
|-
!Name
!Type
!City
!Notes
|-
|Stronghold Games
|Store
|Hull
|[https://www.facebook.com/strongholdgamesLTD/ Facebook]
|-
|Geek Retreat Leeds
|Store
|Leeds
|Chainbound on Thursday evenings. Food and drink served. [https://www.facebook.com/GeekRetreatLeeds Facebook]
|-
|[https://www.patriotgames.ltd.uk/about-us.php Patriot Games]
|Store
|Sheffield
|Chainbound on Monday evenings. 
|-
|Keyforge Hull 
|Group
|Hull
|[https://www.facebook.com/groups/413647409406188/ Facebook]
|-
|KeyForge Leeds 
|Group
|Leeds
|[https://www.facebook.com/groups/2445756608786197/ Facebook], [https://twitter.com/KeyforgeLeeds Twitter]
|-
|The Howling Pit 
|Group
|Sheffield
|[https://www.facebook.com/groups/2395116027240646/ Facebook]
|}

==North America, Central America, and The Carribean==
===Canada===
===Mexico===
===United States===
====California====
{| class="wikitable sortable"
|-
! colspan="4" | Bay Area 
|-
! Name||Type||City||Notes
|-
| [https://ancientbearrepublic Ancient Bear Republic] || Group || || [https://discord.gg/xgYruhFKRh Discord]
|-
| [https://eudemonia.net Eudemonia] || Shop || Berkeley || Chainbound (Sunday), Weekly Sealed (Sunday) (On hold due to COVID-19)
|-
| [https://www.gamescapesf.com Gamescape SF] || Shop ||San Francisco|| Thursdays (On hold due to COVID-19)
|-
| [https://www.illusive-isle.com/ Isle of Gamers] || Shop || Santa Clara || [https://discord.gg/n4V9z3G Discord] [https://www.facebook.com/groups/208216823433104/ Facebook]
|-
| [https://kingkongcomicsandgames.com/ King Kong Comics and Games] || Shop || Pleasanton ||  [https://discord.gg/88hM5d4 Discord]
|-
| [https://victorypointcafe.com Victory Point Cafe] || Cafe || Berkeley || KeyForge on Tuesdays (On hold due to COVID-19)
|}

{| class="wikitable sortable"
|-
! colspan="4" | Southern California 
|-
! Name||Type||City||Notes
|-
| At Ease Games || Shop || San Diego || Chainbound (Thursdays) [https://www.facebook.com/ateasegames/ Facebook]
|- 
| [https://www.geekyteas.com/ Geeky Teas and Games] || Shop || Burbank || 
|-
| [https://www.itsgametimela.com/ It's Game Time] || Shop || Los Angeles || 
|-
| [https://pairadicegames.com/ Pair a Dice Games] || Shop || Vista || Weekly Sealed (Fridays) Chainbound (Saturdays) (On hold due to COVID-19)
|}

====Maryland====
{| class="wikitable sortable"
|-
! Name||Type||City||Notes
|-
| [https://gamesandstuff.com/ Games and Stuff] || Shop || Glen Burnie ||KeyForge on Mondays. [https://www.facebook.com/gamesandstuff Facebook] 
|- 
| KeyForge Baltimore || Group || Baltimore ||  [https://www.facebook.com/groups/293097797938145 Facebook]  [https://discord.gg/3mY6VQJPKA Discord]
|-
| [https://cantongames.com/ Canton Games] || Shop ||Baltimore||Monthly KeyForge events 
|}

====Washington, DC====
{| class="wikitable sortable"
|-
! Name||Type||City||Notes
|-
| Dice City || Shop || DC ||KeyForge on Mondays [https://www.facebook.com/dicecity/  Facebook]
|- 
| [https://www.labyrinthgameshop.com/ Labrynth Game Shop] || Shop || DC ||  Occasional KeyForge Events
|}

====Wisconsin====
{| class="wikitable sortable"
|-
! Name||Type||City||Notes
|-
|Coloseum Games	||Shop||Kenosha||[https://discord.gg/Cp96VcCpvS Discord]
|-
|Keyforge Milwaukee ||	Group || Milwaukee|| [https://www.facebook.com/groups/415789268962139 Facebook]
|-
|Keyforge Wisconsin ||	||Group||[https://www.facebook.com/groups/Keyforge.WI Facebook]
|-
|Kryptonite Kollectibes	|| Shop	|| Janesville || [https://discord.gg/7PeDh252th Discord]
|}

==South America==


{{SEO}}
[[Category:Supplements]]

"""

def write(mwm):
    rows = parse_tables(text)
    for row in rows:
        print(mwm.write_page(row.page_name, row.output_text(), "Building local scene tables"))