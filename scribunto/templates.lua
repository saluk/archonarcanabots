--Module:LuacardTemplates

--[[ Guidelines for this template:

A note on how it is called:
This template is rendered by Module:Luacard, which will replace any text
surrounded by "${}". That text is then rendered as a normal mediawiki template.

Uses a variant of moustache (https://mustache.github.io/mustache.5.html) for
inserting variables from cargo. The differences from the spec are, you wrap
variables in ${} instead of {{ }}. This is to enable you to still use 
{{ }} for mediawiki templates. The other difference is variables are NOT
html escaped by default. Most of the time, we are outputting html, so it
didn't make sense to force us to specify that every time we want it.

Examples of handy things from moustache:

  Just render a variable:
  ${some_variable}

  Rendering a section for each item in a list:

  ${#list}
    ${item_variable 1}
    ${item_variable 2}
  ${/list}

  Similarly, only rendering a section if a boolean is true:

  ${#is_true}
    Render me only if is_true... is true!
  ${/is_true}

  You can also render something only if a list is empty or if is_true is false:

  ${^is_true}
    Render me only if is_true... is false
  {/is_true}

  ${^empty_list}
    Looks like there was nothing in that there list
  ${/empty_list}


Variables passed to this template:

cardstyle = imported css from Module:LuacardStyle

card fields
-----------
cardname = (translated) name of card
cardname_e = english name of card
cardhouse = house of card
cardhouse_t = translated house of card
cardtype = type of card
cardtype_t = translated type of card
cardrarity = rarity of card
cardrarity_t = translated rarity of card
cardtext = base (translated) text of card as its in the mastervault
cardflavortext = base (translated) text of the card as its in the master vault
cardartist = english name of artist (don't think we will translate this field?)
cardimage = the base (translated) image
errata_text = the most recent errata text (todo: not translated)
errata_version = the version the errata was recently updated in (todo: not translated)
original_text = the original version of the text (todo: not translated)

terms
-----
word_power_t = 'power' for english
word_armor_t = 'armor' for english
word_artist_t = 'artist' for english

stylistic variables
-------------------
cardhouse_color = blank for multi house, lowercase house name otherwise, used to style the border

some booleans controlling output
--------------------------------
artdefault = show the card image in the general case
is_amber_vault = show "dark amber vault" multihouse image  (todo: the general case could handle these)
is_its_coming = show "it's coming" multihouse image
is_multi = card has multiple houses, used for house display
is_anomaly = used to display the house image for anomalies, because the icon is a different size
cardstats = if the card has any valid stats to be shown
has_carderrata = if the card has errata
has_ruleofficial = has official rulings (faq, or ffgruling) (todo: not translated. todo: combine all rule displays into one template)
has_rulecommentary = has commentary rulings  (wont be translated)
has_ruleoutstanding = has outstanding rulings  (wont be translated)

lists of data
-------------
note: all lists of data have these special fields:
delim: true for each item of the list except the last one, used to put text between items

cardsets = list of:
  shortset_from_name = the abbreviation of the set (MM) or the set logo for translated pages
  SetData.CardNumber = the number in that set for this card
altart = list of alternate art images, used to override image display
  CardData.Image = standard card image  (todo: maybe these should just use cardimage/cardname)
  CardData.Name = standard card name  (todo: maybe these should just use cardimage/cardname)
  AltArt.File = image source for the alternate image file
cardstatpower = shown for creatures with valid power stat
  min = minimum available power value to link to search (if the card power is too high we have to pass "10+")
  max = maximum available power value to link to search
  value = the power value for this card
cardstatarmor = shown for creatures with valid armor stat
  min = minimum available power value to link to search (if the card power is too high we have to pass "10+")
  max = maximum available power value to link to search
  value = the power value for this card
cardstatamber = shown for cards with bonus amber
  min = minimum available power value to link to search (if the card power is too high we have to pass "10+")
  max = maximum available power value to link to search
  value = the power value for this card
cardtraits = list of traits
  . = the english trait word
  translate_trait = the translated trait word
ruleofficial = list of faq or ffg rulings
  RulesType = ruling type
  RulesText = rules text
  RulesSource = rules source
rulecommentary = list of commentary rulings
  RulesType = ruling type
  RulesText = rules text
  RulesSource = rules source
ruleoutstanding = list of outstanding issue rulings
  RulesType = ruling type
  RulesText = rules text
  RulesSource = rules source
--]]


local template_base = [==[
<html><style type="text/css">${cardstyle}</style></html>

${^locale}
<html><span class="pageOverlay">
${cardname} • ${cardhouse} • ${cardtype} • ${cardrarity} • </html>${cardtext}<html> • Artist: ${cardartist} • Card Number: ${#cardsets}</html>${shortset_from_name}<html>:${SetData.CardNumber}${#delim},&nbsp;${/delim}${/cardsets}
</span></html>
${/locale}

{{Sharing}}

<div class="cardEntry">
  <html>
  ${#art_default}
    <div class="image">
      </html>[[File:${cardimage}|300px|frameless|alt=${cardname}]]<html>
    </div>
  ${/art_default}

  ${#is_amber_vault}
      </html>
      {{Multi House
      |Name={{{Name}}}
      |House1=Dis
      |Image1=479-001-Dis.png
      |House2=Logos
      |Image2=479-001-Logos.png
      |House3=Sanctum
      |Image3=479-001-Sanctum.png
      |House4=Saurian
      |Image4=479-001-Saurian.png
      |House5=Shadows
      |Image5=479-001-Shadows.png
      |House6=Star Alliance
      |Image6=479-001-Star_Alliance.png
      |House7=Untamed
      |Image7=479-001-Untamed.png
      }}
      <html>
  ${/is_amber_vault}

  ${#is_its_coming}
    </html>
    {{Multi House
    |Name={{{Name}}}
    |House1=Logos
    |Image1=479-117-Logos.png
    |House2=Saurian
    |Image2=479-117-Saurian.png
    |House3=Untamed
    |Image3=479-117-Untamed.png
    }}
    <html>
  ${/is_its_coming}

  ${#altart}
    <div class="largeBackground"><div id="wrap"><ul id="gallery-container">
      <li class="gallery-item">
        <input checked="checked" type="radio" name="gallery-list" class="gallery-selector" value="1.jpg" id="gallery-item1" />
        <div class="gallery-fullsize">
          </html>[[File:${CardData.Image}|300px|frameless|alt=${CardData.Name} Regular Art]]<html>
        </div>
        <label for="gallery-item1" class="gallery-label1">Default</label>
      </li>
      <li class="gallery-item">
        <input type="radio" name="gallery-list" class="gallery-selector" value="2.jpg" id="gallery-item2" />
        <div class="gallery-fullsize">
          </html>[[File:${AltArt_File}|300px|frameless|alt=${CardData.Name} Alternate Art]]<html>
        </div>
        <label for="gallery-item2" class="gallery-label2">Alt-Art</label>
      </li></ul></div></div>
      </html><includeonly>[[Category:Alternate_Art]]</includeonly><html>
  ${/altart}
  </html>

  <div class="rightSide">
    <div class="topRow">
      <div class="house ${cardhouse_color}">
        ${#is_multi}Multi${/is_multi}
        ${^is_multi}
          ${#is_anomaly}{{House|House=${cardhouse}|Size=20px}} <html><a href="https://archonarcana.com/Card_Gallery?houses=${cardhouse}">${cardhouse_t}</a></html>${/is_anomaly}
          ${^is_anomaly}{{House|House=${cardhouse}|Size=25px}} [[Houses#${cardhouse}|${cardhouse_t}]]${/is_anomaly}
        ${/is_multi}
      </div>
      <div class="type ${cardhouse_color}"><html><a href="https://archonarcana.com/Card_Gallery?types=${cardtype}">${cardtype_t}</a></html></div>
      <div class="rarity ${cardhouse_color}">{{Rarity|Rarity=${cardrarity}|Size=20px}} <html><a href="https://archonarcana.com/Card_Gallery?rarities=${cardrarity}">${cardrarity_t}</a></html></div>
    </div>


    <div class="creatureRow">
      ${#cardstatpower}
        <div class="power"><html>
          <a href="/Card_Gallery?types=Creature&power_min=${cardstatpower.min}&power_max=${cardstatpower.max}"></html>
            ${cardstatpower.value} ${word_power_t}<html>
          </a>
        </html></div>
      ${/cardstatpower}

      ${#cardstatarmor}
        <div class="armor"><html>
        <a href="/Card_Gallery?types=Creature&armor_min=${cardstatarmor.min}&armor_max=${cardstatarmor.max}"></html>
        ${cardstatarmor.value} ${word_armor_t}<html></a></html></div>
      ${/cardstatarmor}

      ${#cardstatamber}
        <div class="aember"><html>
        <a href="/Card_Gallery?amber_min=${cardstatamber.min}&amber_max=${cardstatamber.max}"></html>
        ${cardstatamber.value} {{Aember}}<html></a></html></div>
      ${/cardstatamber}

      ${#cardstats}
        <div class="spacer"></div>
      ${/cardstats}
    </div>

    <div class="traits">
    ${#cardtraits}
    <html><a href="https://archonarcana.com/Card_Gallery?traits=${.}">${translate_trait}</a></html>
    ${#delim} • ${/delim}
    ${/cardtraits}
    </div>

    <div class="cardText">
    ${^has_carderrata}
      <span class="plainlinks">
        ${cardtext}
      </span>
    ${/has_carderrata}

    ${#has_carderrata}
      <html><ul id="gallery-containerErrata">
        <div class="horizontalLine"></div>
        <li class="gallery-itemErrata">
          <input checked="checked" type="radio" name="gallery-listErrata" class="gallery-selectorErrata" value="1.jpg" id="gallery-item1Errata" />
          <div class="gallery-fullsizeErrata"></html>${errata_text}<html></div>
          <label for="gallery-item1Errata" class="gallery-label1Errata">Current Text</label>
        </li>
        <li class="gallery-itemErrata">
          <input type="radio" name="gallery-listErrata" class="gallery-selectorErrata" value="2.jpg" id="gallery-item2Errata" />
          <div class="gallery-fullsizeErrata"></html><i>${cardname} was updated in ${errata_version}. Original card text:</i><p>${original_text}<html></div>
          <label for="gallery-item2Errata" class="gallery-label2Errata">Original Text</label>
        </li>
      </ul></html>
    ${/has_carderrata}
    </div>

    <div class="flavorText">
    ${cardflavortext}
    </div>

    <div class="sets">
    ${#cardsets}
      <div class="setEntry"><b>${shortset_from_name}</b> ${SetData.CardNumber}</div>
    ${/cardsets}
    </div>

    <div class="artist"><b>${word_artist_t}</b>: [[${cardartist}]]</div>
  </div>
</div>

  ${#has_ruleofficial}<h2>FFG Rulings</h2>${/has_ruleofficial}
  ${#ruleofficial}
  {{ FAQ_Entry|RulesType=${RulesType}|RulesText=${RulesText}|RulesSource=${RulesSource} }}
  ${/ruleofficial}

  ${#has_rulecommentary}<h2>Commentary</h2>${/has_rulecommentary}
  ${#rulecommentary}
  {{ Commentary_Entry|RulesType=${RulesType}|RulesText=${RulesText}|RulesSource=${RulesSource} }}
  ${/rulecommentary}

  ${#has_ruleoutstanding}<h2>Outstanding Issues</h2>${/has_ruleoutstanding}
  ${#ruleoutstanding}
    {{ Commentary_Entry|RulesType=${RulesType}|RulesText=${RulesText}|RulesSource=${RulesSource} }}
  ${/ruleoutstanding}

__NOTOC__
${categories}
{{SEO}}
]==]

return {
    template_base = template_base
}