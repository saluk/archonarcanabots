--Module:LuacardTemplates
local template_base = [==[
<html>
<style type="text/css">
${cardstyle}
</style>
<span class="pageOverlay">
${cardname} • ${cardhouse} • ${cardtype} • ${cardrarity} • ${cardtext} • Artist: ${cardartist} • Card Number: ${cardnumber_short}
</p></span>
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
  </div>



</div>
]==]

local rest = [==[
{{#ifeq: {{{Type}}}|Creature|<div class="creatureRow"><div class="power">{{#ifexpr: {{{Power}}} > 9 |<html><a href="https://archonarcana.com/Card_Gallery?types=Creature&power_min=10+&power_max=10+"></html>{{{Power}}} Power<html></a></html>|<html><a href="https://archonarcana.com/Card_Gallery?types=Creature&power_min=</html>{{{Power}}}<html>&power_max=</html>{{{Power}}}<html>"></html>{{{Power}}} Power<html></a></html>}}</div>
    <div class="armor">{{#if: {{{Armor|}}}| {{#ifexpr: {{{Armor}}}>4|<html><a href="https://archonarcana.com/Card_Gallery?types=Creature&armor_min=5+&armor_max=5+"></html>{{{Armor}}} Armor<html></a></html>|<html><a href="https://archonarcana.com/Card_Gallery?types=Creature&armor_min=</html>{{{Armor}}}<html>&armor_max=</html>{{{Armor}}}<html>"></html>{{{Armor}}} Armor<html></a></html>}} |<html><a href="https://archonarcana.com/Card_Gallery?types=Creature&armor_min=0&armor_max=0"></html>0 Armor</html></a></html>}}</div>
{{#ifeq: {{{Amber}}}|0|| {{#ifexpr: {{{Amber}}} < 4|<div class="aember"><html><a href="https://archonarcana.com/Card_Gallery?amber_min=</html>{{{Amber}}}<html>&amber_max=</html>{{{Amber}}}<html>"></html>{{{Amber}}}{{Aember}}<html></a></html></div>|<div class="aember"><html><a href="https://archonarcana.com/Card_Gallery?amber_min=4+&amber_max=4+"></html>{{{Amber}}}{{Aember}}<html></a></html></div>}} }}</div>
| {{#ifeq: {{{Amber}}}|0|<div class="spacer"></div>|<div class="creatureRow"><div class="aember">{{#ifexpr: {{{Amber}}} < 4|<html><a href="https://archonarcana.com/Card_Gallery?amber_min=</html>{{{Amber}}}<html>&amber_max=</html>{{{Amber}}}<html>"></html>{{{Amber}}}{{Aember}}<html></a></html>|<html><a href="https://archonarcana.com/Card_Gallery?amber_min=4+&amber_max=4+"></html>{{{Amber}}}{{Aember}}<html></a></html>}}</div></div>}} }}
  <div class="traits">{{#if: {{{Traits|}}}|{{#vardefine: i | 0 }}{{#while: | {{#ifexpr: {{#var: i }} < 9 | true }} | <nowiki /> {{#vardefine: y |{{#explode:{{{Traits}}}|<nowiki> </nowiki>|{{#var: i }}}} }} {{#if: {{#var: y }}|{{#ifeq: {{#var: y }}|•|•|<html><a href="https://archonarcana.com/Card_Gallery?traits=</html>{{#var: y }}<html>"></html>{{#var: y }}<html></a></html>}}|}}{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }} }}|}}</div>
{{Errata Text
|Name={{{Name}}}
|CurrentText={{{Text}}}
|OriginalText={{#cargo_query:
tables=CardData, ErrataData
|fields=ErrataData.Text
|where=ErrataData._ID is not null AND CardData.Name='{{{Name}}}'
|join on=CardData._pageName=ErrataData._pageName
|order by=ErrataData._ID ASC
|limit=1
|default=
|more results text=}}
|Version={{#cargo_query:
tables=CardData, ErrataData
|fields=ErrataData.Version
|where=ErrataData._ID is not null AND CardData.Name='{{{Name}}}'
|join on=CardData._pageName=ErrataData._pageName
|order by=ErrataData._ID DESC
|limit=1
|default=
|more results text=}}}}
  <div class="flavorText">{{{FlavorText|}}}</div>
{{#cargo_query:
tables=SetData,CardData,SetInfo
|fields=SetData.SetName, SetData.CardNumber=, SetInfo.ReleaseYear, SetInfo.ReleaseMonth
|join on=SetData._pageTitle=CardData.Name,SetData.SetName=SetInfo.SetName
|where=CardData.Name='{{{Name}}}'
|format=template
|template=Card_Sets
|default=
|intro=<div class="sets">
|outro=</div>
|order by=SetInfo.ReleaseYear, SetInfo.ReleaseMonth
}}
  <div class="artist"><b>Artist</b>: [[{{{Artist|}}}]]</div>
</div>
</div>
__NOTOC__{{#cargo_query:
tables=SetData,CardData
|fields=SetData.SetName
|join on=SetData._pageTitle=CardData.Name
|where=CardData.Name='{{{Name}}}'
|format=template
|template=Card_Categories
}}{{#if: {{{Traits|}}} |{{#if: {{#explode:{{{Traits}}}|<nowiki> </nowiki>|0}}|[[Category:{{#explode:{{{Traits}}}|<nowiki> </nowiki>|0}}]]|}} 
{{#if: {{#explode:{{{Traits}}}|<nowiki> </nowiki>|2}}|[[Category:{{#explode:{{{Traits}}}|<nowiki> </nowiki>|2}}]]|}} 
{{#if: {{#explode:{{{Traits}}}|<nowiki> </nowiki>|4}}|[[Category:{{#explode:{{{Traits}}}|<nowiki> </nowiki>|4}}]]|}} 
{{#if: {{#explode:{{{Traits}}}|<nowiki> </nowiki>|6}}|[[Category:{{#explode:{{{Traits}}}|<nowiki> </nowiki>|6}}]]|}} 
{{#if: {{#explode:{{{Traits}}}|<nowiki> </nowiki>|8}}|[[Category:{{#explode:{{{Traits}}}|<nowiki> </nowiki>|8}}]]|}} |}}
{{#if: {{#pos:{{{Text}}}|{{PAGENAME}}|offset}}|[[Category:Self-referential]]|}}
<includeonly>[[Category:{{{Type}}}]] {{#ifeq: {{#rpos:{{{House}}}|•}}|-1|[[Category:{{{House}}}]]|[[Category:Multi]]}} [[Category:{{{Rarity}}}]] [[Category:Card]] {{SEO}}</includeonly><nowiki>








</nowiki>{{#cargo_query:
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