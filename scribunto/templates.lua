--Module:LuacardTemplates
local template_base = [==[
<html>
<style type="text/css">
${cardstyle}
</style>

<span class="pageOverlay">${cardname} • ${cardhouse} • ${cardtype} • ${cardrarity} • ${cardtext_short} • Artist: </html>${cardartist}<html> • Card Number: ${#cardsets}</html>${shortset_from_name}<html>:${SetData.CardNumber}${#delim},&nbsp;${/delim}${/cardsets}
</span>
</html>
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
      ${cardtext}
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