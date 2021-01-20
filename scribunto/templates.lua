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
      <div class="house ${cardhouse_lower}">
        ${cardhouse_section}
      </div>
      <div class="type"><html><a href="https://archonarcana.com/Card_Gallery?types=${cardtype}">${cardtype}</a></html></div>
      <div class="rarity">{{Rarity|Rarity=${cardrarity}|Size=20px}} <html><a href="https://archonarcana.com/Card_Gallery?rarities=${cardrarity}">${cardrarity}</a></html></div>
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

__NOTOC__
${categories}
{{SEO}}
]==]

local rest = [==[
  {{#cargo_query:
tables=RuleData
|fields=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|where=((RulesText like '%{{{Name}}}%' AND RulesPages IS NULL) OR (RulesPages like '%•{{{Name}}}•%')) AND RulesType='FAQ'
|limit=100
|offset=0
|format=template
|template=FAQ_Entry
|order by=RulesDate ASC
|group by=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|named args=yes
|no html
|max display chars=10000
|intro=<h2>FFG Rulings</h2>
|outro=<includeonly>[[Category:FAQ]]</includeonly>
|default=
}}{{#cargo_query:
tables=RuleData
|fields=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|where=((RulesText like '%{{{Name}}}%' AND RulesPages IS NULL) OR (RulesPages like '%•{{{Name}}}•%')) AND RulesType='FFGRuling'
|limit=100
|offset=0
|format=template
|template=FAQ_Entry
|order by=RulesDate ASC
|group by=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|named args=yes
|no html
|max display chars=10000
|intro={{#cargo_query:
tables=RuleData
|fields=CONCAT('')
|where=((RulesText like '%{{{Name}}}%' AND RulesPages IS NULL) OR (RulesPages like '%•{{{Name}}}•%')) AND RulesType='FAQ'
|limit=1
|more results text=
|default=<h2>FFG Rulings</h2>}} 
|outro=<includeonly>[[Category:FFG Rulings]]</includeonly>
|default=
}}{{#cargo_query:
tables=RuleData
|fields=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|where=((RulesText like '%{{{Name}}}%' AND RulesPages IS NULL) OR (RulesPages like '%•{{{Name}}}•%')) AND RulesType='Commentary'
|limit=100
|offset=0
|format=template
|template=Commentary_Entry
|order by=RulesDate ASC
|group by=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|named args=yes
|no html
|max display chars=10000
|intro=<h2>Commentary</h2>
|outro=<includeonly>[[Category:Commentary]]</includeonly>
|default=
}}{{#cargo_query:
tables=RuleData
|fields=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|where=(((RulesText like '%{{{Name}}}%' AND RulesPages IS NULL) OR (RulesPages like '%•{{{Name}}}•%')) AND RulesType='OutstandingIssues') AND (RulesText like '%//%')
|limit=100
|offset=0
|format=template
|template=Commentary_Entry
|order by=RulesDate ASC
|group by=RulesText, RulesType, RulesSource, RulesPages, RulesDate
|named args=yes
|no html
|max display chars=10000
|intro=<h2>Outstanding Issues</h2><div class="aa-box">[[File:Exclamation_flat_icon.svg|20px|class=aa-warning|frameless|link=]]<div class="text">There is an outstanding issue concerning {{{Name}}}. </div></div>
|outro=<includeonly>[[Category:Commentary]]</includeonly>
|default=
}}
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