--Module:Luacard
local p = {}
local cargo = mw.ext.cargo

local templates = require('Module:LuacardTemplates')
local cardstyle = require('Module:LuacardStyle')
local translations = require('Module:LocaleTable')

local translate_table = {}

local translate = function(word)
	if(translate_table[word]~=nil) then
		return translate_table[word]
	else
		return word
	end
end

function interp(s, tab)
	local trans_tab = {}
	for k,v in pairs(tab) do
		trans_tab[k..'_t'] = translate(v)
	end
	return (s:gsub('($%b{})', function(w) return trans_tab[w:sub(3,-2)] or tab[w:sub(3, -2)] or w end))
end

function wikitext(s)
	return s:gsub('\n', ''):gsub('<p>','__PARA__')
end

function dewikitext(s)
	return s:gsub('__PARA__', '<p>')
end

local set_category = {}
set_category['Call of the Archons']='CotA'
set_category['Age of Ascension']='AoA'
set_category['Worlds Collide']='WC'
set_category['Mass Mutation']='MM'
set_category['Dark Tidings']='DT'
set_category['Worlds Collide-Anomaly']='WC-A'
set_category['Anomaly']='WC-A'

local shortset = function(longset)
	local sets = {}
	sets['Call of the Archons']='CotA'
	sets['Age of Ascension']='AoA'
	sets['Worlds Collide']='WC'
	sets['Mass Mutation']='MM'
	sets['Dark Tidings']='DT'
	local args = {longset = longset, shortset=sets[longset]}
	return interp('[[${longset}|${shortset}]]', args)
end

local translate_trait = function(frame, type, word)
	if(frame.args.locale) then
		return mw.ustring.upper(translations[type][frame.args.locale][mw.ustring.lower(word)])
	else
		return word
	end
end

local load_translation_table = function(locale)
	local translate_table_results = cargo.query(
		'TranslationTable',
		'EnglishText,Type,TranslatedText',
		{
			where='Locale="'..locale..'"'
		})
	for r=1, #translate_table_results do
		local result = translate_table_results[r]
		translate_table[result.EnglishText] = result.TranslatedText
	end
end

local apply_altart = function(frame, vars)
	if(vars.cardname == 'Dark Æmber Vault') then
		vars.cardart = [==[
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
		]==]
		return
	elseif(vars.cardname == 'It’s Coming...') then
		vars.cardart = [==[
			{{Multi House
			|Name={{{Name}}}
			|House1=Logos
			|Image1=479-117-Logos.png
			|House2=Saurian
			|Image2=479-117-Saurian.png
			|House3=Untamed
			|Image3=479-117-Untamed.png
			}}
		]==]
		return
	end
	local altart_results = cargo.query(
		'AltArt,CardData',
		'AltArt.File,CardData.Image,CardData.Name',
		{
			join='AltArt._pageTitle=CardData.Name',
			where='CardData.Name="'..vars.cardname..'"'
		}
	)
	if(#altart_results == 0) then
		vars.cardart = interp(templates.template_art, vars)
	end
	for r = 1, #altart_results do
		local result=altart_results[r]
		if(result['AltArt.File'] ~= nil) then
			vars.cardart = interp(templates.template_altart, result)
		else
			vars.cardart = interp(templates.template_art, vars)
		end
	end
end

function apply_house(frame, vars)
	if(vars.cardhouse:find('•', 1, true)) then
		vars.cardhouse_section = 'Multi'
		vars.cardhouse_color = ''
		vars.categories[#vars.categories+1] = 'Multi'
	else
		vars.cardhouse_color = vars.cardhouse_lower
		vars.categories[#vars.categories+1] = vars.cardhouse
		local size = '25'
		if(vars.cardhouse:find('Anomaly')) then
			vars.cardhouse_section = '{{House|House=${cardhouse}|Size=20px}} <html><a href="https://archonarcana.com/Card_Gallery?houses=${cardhouse}">${cardhouse_t}</a></html>'
		else
			vars.cardhouse_section = '{{House|House=${cardhouse}|Size=25px}} [[Houses#${cardhouse}|${cardhouse_t}]]'
		end
	end
	vars.cardhouse_section = interp(vars.cardhouse_section, vars)
end

function minmax_arg(value, max)
	value = tonumber(value)
	if(value > max-1) then
		return {min=tostring(max)..'+', max=tostring(max)..'+', value=value}
	else
		return {min=tostring(value), max=tostring(value), value=value}
	end
end

function apply_stats(frame, vars)
	vars.cardstatamber = ''
	vars.cardstatpower = ''
	vars.cardstatarmor = ''
	if(vars.cardtype == 'Creature' and string.len(vars.cardpower)>0 and tonumber(vars.cardpower) >= 0) then
		local mm = minmax_arg(vars.cardpower, 10)
		vars.min = mm.min
		vars.max = mm.max
		vars.value = mm.value
		local t = '<div class="power"><html><a href="/Card_Gallery?types=Creature&power_min=${min}&power_max=${max}"></html>${value} ${word_power_t}<html></a></html></div>'
		vars.cardstatpower = interp(t, vars)
	end
	if(vars.cardtype == 'Creature' and string.len(vars.cardarmor)>0 and tonumber(vars.cardarmor) >= 0) then
		local mm = minmax_arg(vars.cardarmor, 5)
		vars.min = mm.min
		vars.max = mm.max
		vars.value = mm.value
		local t = '<div class="armor"><html><a href="/Card_Gallery?types=Creature&armor_min=${min}&armor_max=${max}"></html>${value} ${word_armor_t}<html></a></html></div>'
		vars.cardstatarmor = interp(t, vars)
	end
	if(string.len(vars.cardamber)>0 and tonumber(vars.cardamber) >= 1) then
		local mm = minmax_arg(vars.cardamber, 4)
		local t = '<div class="aember"><html><a href="/Card_Gallery?amber_min=${min}&amber_max=${max}"></html>${value} {{Aember}}<html></a></html></div>'
		vars.cardstatamber = interp(t, mm)
	end
	if(vars.cardstatamber.len==0 and vars.cardstatpower==0 and vars.cardstatarmor==0) then
		vars.cardstatamber = '<div class="spacer"></div>'
	end
end

function apply_traits(frame, vars)
	if(string.len(mw.text.trim(vars.cardtraits))==0) then
		return
	end
	local split = mw.text.split(vars.cardtraits, ' • ')
	local out = {}
	for i = 1, #split do
		out[i] = interp(
			'<html><a href="https://archonarcana.com/Card_Gallery?traits=${cur}">${name}</a></html>',
			{
				cur=split[i],
				name=translate_trait(frame, 'traits', split[i])
			}
		)
		vars.categories[#vars.categories+1] = split[i]
	end
	vars.cardtraits = table.concat(out, ' • ')
end

function apply_categories(frame, vars)
	for c=1, #vars.categories do
		if(string.len(mw.text.trim(vars.categories[c]))>0) then
			vars.categories[c] = interp('[[Category:${c}]]', {c=vars.categories[c]})
		end
	end
	vars.categories = '<includeonly>'..table.concat(vars.categories,'')..'</includeonly>'
end

function rulequery(type, cardname)
	return cargo.query(
		'RuleData',
		'RulesText, RulesType, RulesSource, RulesPages, RulesDate',
		{
			groupBy='RulesText, RulesType, RulesSource, RulesPages, RulesDate',
			where="((RulesText like '%"..cardname.."%' AND RulesPages IS NULL) OR (RulesPages like '%•"..cardname.."•%')) AND RulesType='"..type.."'",
			orderBy='RulesDate ASC'
		})
end

function apply_rulings(frame, vars)
	vars.ruleofficial = ''
	vars.rulecommentary = ''
	vars.ruleoutstanding = ''

	local official_results = rulequery('FAQ', vars.cardname)
	if(#official_results>0) then vars.categories[#vars.categories+1] = 'FAQ' end

	local ruling_results = rulequery('FFGRuling', vars.cardname)
	if(#ruling_results>0) then vars.categories[#vars.categories+1] = 'FFG Rulings' end

	for _,v in ipairs(ruling_results) do
		table.insert(official_results, v)
	end

	local commentary_results = rulequery('Commentary', vars.cardname)
	local outstanding_results = rulequery('OutstandingIssues', vars.cardname)
	if(#outstanding_results>0 or #commentary_results>0) then vars.categories[#vars.categories+1] = 'Commentary' end

	if(#official_results>0) then
		vars.ruleofficial = vars.ruleofficial .. '<h2>FFG Rulings</h2>'
		for i,v in ipairs(official_results) do
			vars.ruleofficial = vars.ruleofficial .. frame:expandTemplate{title='FAQ_Entry', args={
				RulesType=v['RulesType'],
				RulesText=v['RulesText'],
				RulesSource=v['RulesSource']
			}}
		end
	end
	if(#commentary_results>0) then
		vars.rulecommentary = vars.rulecommentary .. '<h2>Commentary</h2>'
		for i,v in ipairs(commentary_results) do
			vars.rulecommentary = vars.rulecommentary .. frame:expandTemplate{title='Commentary_Entry', args={
				RulesType=v['RulesType'],
				RulesText=v['RulesText'],
				RulesSource=v['RulesSource']
			}}
		end
	end
	if(#outstanding_results>0) then
		vars.ruleoutstanding = vars.ruleoutstanding .. '<h2>Outstanding Issues</h2><div class="aa-box">[[File:Exclamation_flat_icon.svg|20px|class=aa-warning|frameless|link=]]<div class="text">There is an outstanding issue concerning {{{Name}}}. </div></div>'
		for i,v in ipairs(outstanding_results) do
			if(v['RulesText'].find('//')) then
				vars.ruleoutstanding = vars.ruleoutstanding .. frame:expandTemplate{title='Commentary_Entry', args={
					RulesType=v['RulesType'],
					RulesText=v['RulesText'],
					RulesSource=v['RulesSource']
				}}
			end
		end
	end
end

function p.viewcard(frame)
	vars = {
		cardname = frame.args.cardname,
		cardhouse = '',
		cardrarity = 'Rare',
		cardtext = 'Some text',
		cardartist = 'Some artist',
		cardstyle = cardstyle.cardstyle,
		multihouse_style = cardstyle.multihouse_style
	}
	local card_results = cargo.query(
		'CardData',
		'Name,Image,Artist,Text,FlavorText,Type,Rarity,House,Traits,Power,Armor,Amber',
        {
			where='CardData.Name="'..frame.args.cardname..'"'
		})
	if(frame.args.locale) then
		load_translation_table(frame.args.locale)
	end
	vars.word_power = 'Power'
	vars.word_armor = 'Armor'
	vars.word_artist = 'Artist'
    vars.cardimage = card_results[1]['Image']
	vars.cardhouse = card_results[1]['House']
	vars.cardhouse_lower = vars.cardhouse:lower()
	vars.cardrarity = card_results[1]['Rarity']
	vars.cardtext_short = wikitext(card_results[1]['Text'])
	vars.cardtext = vars.cardtext_short
	vars.cardflavortext = wikitext(card_results[1]['FlavorText'])
	vars.cardartist = card_results[1]['Artist']
	vars.cardtype = card_results[1]['Type']
	vars.cardpower = card_results[1]['Power']
	vars.cardarmor = card_results[1]['Armor']
	vars.cardamber = card_results[1]['Amber']
	vars.cardtraits = card_results[1]['Traits']
	vars.categories = {vars.cardtype, vars.cardrarity, 'Card'}
	if(string.find(vars.cardtext,vars.cardname)) then
		vars.categories[#vars.categories+1] = 'Self-referential'
	end

	if frame.args.locale then
		local locale_table_results = cargo.query(
			'CardLocaleData',
			'Name,EnglishName,Text,FlavorText,Locale,Image',
			{
				where='CardLocaleData.EnglishName="'..frame.args.cardname..'" and CardLocaleData.Locale="'..frame.args.locale..'"'
			}
		)
		for c = 1, #locale_table_results do
			local cardlocale = locale_table_results[c]
			vars.cardtext = cardlocale['Text']
			vars.cardname = cardlocale['Name']
			vars.cardflavortext = cardlocale['FlavorText']
			vars.cardimage = cardlocale['Image']
		end
	end
    
	local set_number_results = cargo.query(
		'SetData,CardData,SetInfo',
		'SetData.SetName, SetData.CardNumber, SetInfo.ReleaseYear, SetInfo.ReleaseMonth',
		{
			join='SetData._pageTitle=CardData.Name,SetData.SetName=SetInfo.SetName',
			where='CardData.Name="'..frame.args.cardname..'"',
			orderBy='SetInfo.ReleaseYear, SetInfo.ReleaseMonth'
		})
	local cardnumber_short = {}
	local cardnumber = {}
	for r = 1, #set_number_results do
		local result = set_number_results[r]
		result['short'] = shortset(result['SetData.SetName'])
		cardnumber_short[r] = interp('${short}:${SetData.CardNumber}', result)
		cardnumber[r] = interp('<div class="setEntry"><b>${short}</b> ${SetData.CardNumber}</div>', result)
		vars.categories[#vars.categories+1] = set_category[result['SetData.SetName']]
	end
	vars.cardnumber_short = table.concat(cardnumber_short, ',&nbsp;')
	vars.cardnumber = table.concat(cardnumber, '')
	
	apply_altart(frame, vars)
	apply_house(frame, vars)
	apply_stats(frame, vars)
	apply_traits(frame, vars)

	local errata_results = cargo.query(
		'CardData, ErrataData',
		'ErrataData.Text,ErrataData.Version',
		{
			join='CardData._pageName=ErrataData._pageName',
			where='ErrataData._ID is not null AND CardData.Name="'..vars.cardname..'"',
			orderBy='ErrataData._ID ASC'
		}
	)
	if(#errata_results>0) then
		vars.original_text=wikitext(errata_results[1]['ErrataData.Text'])
		vars.errata_text=wikitext(errata_results[#errata_results]['ErrataData.Text'])
		vars.errata_version = errata_results[#errata_results]['ErrataData.Version']
		if(string.find(vars.errata_version, 'Rulebook')) then
			vars.categories[#vars.categories+1] = 'Errata'
		else
			vars.categories[#vars.categories+1] = 'Revised Cards'
		end
		vars.cardtext = interp([==[
			<html><ul id="gallery-containerErrata"><div class="horizontalLine"></div>
  <li class="gallery-itemErrata">
  	<input checked="checked" type="radio" name="gallery-listErrata" class="gallery-selectorErrata" value="1.jpg" id="gallery-item1Errata" />
		<div class="gallery-fullsizeErrata"></html>${errata_text}<html></div>
		<label for="gallery-item1Errata" class="gallery-label1Errata">Current Text</label>
	</li>
	<li class="gallery-itemErrata">
		<input type="radio" name="gallery-listErrata" class="gallery-selectorErrata" value="2.jpg" id="gallery-item2Errata" />
    <div class="gallery-fullsizeErrata"></html><i>${cardname} was updated in ${errata_version}. Original card text:</i><p>${original_text}<html></div>
		<label for="gallery-item2Errata" class="gallery-label2Errata">Original Text</label>
	</li></ul></html>
		]==], vars)
	else
		if(vars.cardtext=='(Vanilla)') then vars.cardtext=''
		else
			vars.cardtext = '<span class="plainlinks">'..wikitext(vars.cardtext)..'</span>'
		end
	end

	apply_rulings(frame, vars)
	apply_categories(frame, vars)

	text = frame:preprocess(interp(templates.template_base, vars):gsub('\n',''))
	text = dewikitext(text)
	return text
end

return p
