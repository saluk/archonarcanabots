--Module:LuacardTemplates
local template_base = [==[
<html>
<style type="text/css">
${cardstyle}
</style>

<span class="pageOverlay">
${cardname} • ${cardhouse} • ${cardtype} • ${cardrarity} • ${cardtext_short} • Artist: ${cardartist} • Card Number: ${cardnumber_short}
</span>
</html>
{{Sharing}}

<div class="cardEntry">
  ${cardart}

  <div class="rightSide">
    <div class="topRow">
      <div class="house ${cardhouse_color}">
        ${cardhouse_section}
      </div>
      <div class="type ${cardhouse_color}"><html><a href="https://archonarcana.com/Card_Gallery?types=${cardtype}">${cardtype}</a></html></div>
      <div class="rarity ${cardhouse_color}">{{Rarity|Rarity=${cardrarity}|Size=20px}} <html><a href="https://archonarcana.com/Card_Gallery?rarities=${cardrarity}">${cardrarity}</a></html></div>
    </div>


    <div class="creatureRow">
      ${cardstatpower}
      ${cardstatarmor}
      ${cardstatamber}
    </div>

    <div class="traits">
    ${cardtraits}
    </div>

    <div class="cardText">
    ${cardtext}
    </div>

    <div class="flavorText">
    ${cardflavortext}
    </div>

    <div class="sets">
    ${cardnumber}
    </div>

    <div class="artist"><b>Artist</b>: [[${cardartist}]]</div>
  </div>
</div>

  ${ruleofficial}
  ${rulecommentary}
  ${ruleoutstanding}

__NOTOC__
${categories}
{{SEO}}
]==]

local template_altart = [==[
<div class="largeBackground"><div id="wrap"><ul id="gallery-container">
<li class="gallery-item">
        <html><input checked="checked" type="radio" name="gallery-list" class="gallery-selector" value="1.jpg" id="gallery-item1" />
        <div class="gallery-fullsize"></html>[[File:${CardData.Image}|300px|frameless|alt=${CardData.Name} Regular Art]]<html></div>
        <label for="gallery-item1" class="gallery-label1">Default</label>
</li><li class="gallery-item">
    <input type="radio" name="gallery-list" class="gallery-selector" value="2.jpg" id="gallery-item2" />
    <div class="gallery-fullsize"></html>[[File:${AltArt.File}|300px|frameless|alt=${CardData.Name} Alternate Art]]<html></div>
    <label for="gallery-item2" class="gallery-label2">Alt-Art</label></html>
</li></ul></div></div><includeonly>[[Category:Alternate_Art]]</includeonly>
]==]

local template_art = [==[
    <div class="image">[[File:${cardimage}|300px|frameless|alt=${cardname}]]</div>
]==]

return {
    template_base = template_base,
    template_altart = template_altart,
    template_art = template_art
}