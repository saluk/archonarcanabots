--Module:Luacard
local p = {}
local cargo = mw.ext.cargo

function combine(tableto, tablefrom)
	for k,v in pairs(tablefrom) do
		tableto[k] = v
	end
end

function map(table, func)
	for k,v in pairs(table) do
		table[k] = func(v)
	end
	return table
end

function filter(table, func)
	local new = {}
	for k,v in pairs(table) do
		if func(v) then new[k] = v
		end
	end
	return new
end

local templates = require('Module:LuacardTemplates')
local cardstyle = require('Module:LuacardStyle')
local translations = require('Module:LocaleTable')
local luastache = require("Module:luastache")

local translate_table = {}

local translate = function(word)
	if(translate_table[word]~=nil) then
		return translate_table[word]
	else
		return word
	end
end

function insert_translated(tab)
	local trans_tab = {}
	for k,v in pairs(tab) do
		trans_tab[k..'_t'] = translate(v)
	end
	combine(tab, trans_tab)
end

function stachify(table)
	local under_tab = {}
	for k,v in pairs(table) do
		if string.find(k, '[.]') then
			local parts = mw.text.split(k, '[.]')
			if not under_tab[parts[1]] then
				under_tab[parts[1]] = {}
			end
			under_tab[parts[1]][parts[2]] = v
		end
	end
	combine(table, under_tab)
end

function cargo_results(ctable, cfields, cargs)
	local table = cargo.query(ctable, cfields, cargs)
	for i,r in ipairs(table) do
		stachify(r)
		if i<#table then
			r['delim'] = true
		end
	end
	return table
end
	
function stache(s, tab)
	insert_translated(tab)
	stachify(tab)
	s = '{{=${ }=}}'..s
	return luastache:render(s, tab)
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

local shortset = function(longset)
	local sets = {}
	sets['Call of the Archons']='CotA'
	sets['Age of Ascension']='AoA'
	sets['Worlds Collide']='WC'
	sets['Mass Mutation']='MM'
	sets['Dark Tidings']='DT'
	local args = {longset = longset, shortset=sets[longset]}
	return stache('[[${longset}|${shortset_t}]]', args)
end

local translate_trait = function(frame, type, word)
	if(frame.args.locale) then
		if(not translations[type][frame.args.locale]) then
			return word
		end
		return mw.ustring.upper(translations[type][frame.args.locale][mw.ustring.lower(word)])
	else
		return word
	end
end

local load_translation_table = function(locale)
	local translate_table_results = cargo_results(
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
	vars.is_amber_vault = vars.cardname_e == 'Dark Æmber Vault'
	vars.is_its_coming = vars.cardname_e == 'It’s Coming...'
	vars.altart = cargo_results(
		'AltArt,CardData',
		'AltArt.File,CardData.Image,CardData.Name',
		{
			join='AltArt._pageTitle=CardData.Name',
			where='CardData.Name="'..vars.cardname_e..'"'
		}
	)
	vars.art_default = not (vars.is_amber_vault or vars.is_its_coming or #vars.altart>0)
end

function apply_house(frame, vars)
	vars.is_multi = string.find(vars.cardhouse, '•', 1, true)
	vars.is_anomaly = string.find(vars.cardhouse, 'Anomaly')
	if(vars.is_multi) then
		vars.cardhouse_color = ''
		vars.categories[#vars.categories+1] = 'Multi'
	else
		vars.cardhouse_color = vars.cardhouse_lower
		vars.categories[#vars.categories+1] = vars.cardhouse
	end
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
	vars.cardstatamber = {}
	vars.cardstatpower = {}
	vars.cardstatarmor = {}
	if(vars.cardtype == 'Creature' and string.len(vars.cardpower)>0 and tonumber(vars.cardpower) >= 0) then
		vars.cardstatpower = minmax_arg(vars.cardpower, 10)
	end
	if(vars.cardtype == 'Creature' and string.len(vars.cardarmor)>0 and tonumber(vars.cardarmor) >= 0) then
		vars.cardstatarmor = minmax_arg(vars.cardarmor, 5)
	end
	if(string.len(vars.cardamber)>0 and tonumber(vars.cardamber) >= 1) then
		vars.cardstatamber = minmax_arg(vars.cardamber, 4)
	end
	vars.cardstats = vars.cardstatamber.len==0 and vars.cardstatpower==0 and vars.cardstatarmor==0
end

function apply_traits(frame, vars)
	if(string.len(mw.text.trim(vars.cardtraits))==0) then
		return
	end
	local split = mw.text.split(vars.cardtraits, ' • ')
	vars.cardtraits = split
	vars.translate_trait = function(self)
		return translate_trait(frame, 'traits', self)
	end
	for i = 1, #split do
		vars.categories[#vars.categories+1] = split[i]
	end
end

function apply_errata(frame, vars)
	--Use cardname and not cardname_e, because localized errata doesn't exist, we just use the master vault text
	local errata_results = cargo_results(
		'CardData, ErrataData',
		'ErrataData.Text,ErrataData.Version',
		{
			join='CardData._pageName=ErrataData._pageName',
			where='ErrataData._ID is not null AND CardData.Name="'..vars.cardname..'"',
			orderBy='ErrataData._ID ASC'
		}
	)
	if(#errata_results>0) then
		vars.has_carderrata = true
		vars.original_text=wikitext(errata_results[1]['ErrataData.Text'])
		vars.errata_text=wikitext(errata_results[#errata_results]['ErrataData.Text'])
		vars.errata_version = errata_results[#errata_results]['ErrataData.Version']
		if(string.find(vars.errata_version, 'Rulebook')) then
			vars.categories[#vars.categories+1] = 'Errata'
		else
			vars.categories[#vars.categories+1] = 'Revised Cards'
		end
	end
end

function apply_categories(frame, vars)
	for c=1, #vars.categories do
		if(string.len(mw.text.trim(vars.categories[c]))>0) then
			vars.categories[c] = stache('[[Category:${c}]]', {c=vars.categories[c]})
		end
	end
	vars.categories = '<includeonly>'..table.concat(vars.categories,'')..'</includeonly>'
end

function rulequery(type, cardname)
	return cargo_results(
		'RuleData',
		'RulesText, RulesType, RulesSource, RulesPages, RulesDate',
		{
			groupBy='RulesText, RulesType, RulesSource, RulesPages, RulesDate',
			where="((RulesText like '%"..cardname.."%' AND RulesPages IS NULL) OR (RulesPages like '%•"..cardname.."•%')) AND RulesType='"..type.."'",
			orderBy='RulesDate ASC'
		})
end

function apply_rulings(frame, vars)
	-- we use cardname_e and just show english rulings
	local official_results = rulequery('FAQ', vars.cardname_e)
	if(#official_results>0) then vars.categories[#vars.categories+1] = 'FAQ' end

	local ruling_results = rulequery('FFGRuling', vars.cardname_e)
	if(#ruling_results>0) then vars.categories[#vars.categories+1] = 'FFG Rulings' end

	combine(official_results, ruling_results)

	local commentary_results = rulequery('Commentary', vars.cardname_e)
	local outstanding_results = rulequery('OutstandingIssues', vars.cardname_e)
	if(#outstanding_results>0 or #commentary_results>0) then vars.categories[#vars.categories+1] = 'Commentary' end

	vars.has_ruleofficial = #official_results > 0
	vars.ruleofficial = official_results
	vars.has_rulecommentary = #commentary_results > 0
	vars.rulecommentary = commentary_results
	vars.has_ruleoutstanding = #outstanding_results > 0
	vars.ruleoutstanding = filter(outstanding_results, function(ruling)
		if string.find(ruling['RulesText'], '//') then 
			return true 
		else return false 
		end
	end)
end

function apply_sets(frame, vars)
	vars.cardsets = cargo_results(
		'SetData,CardData,SetInfo',
		'SetData.SetName, SetData.CardNumber, SetInfo.ReleaseYear, SetInfo.ReleaseMonth',
		{
			join='SetData._pageTitle=CardData.Name,SetData.SetName=SetInfo.SetName',
			where='CardData.Name="'..frame.args.cardname..'"',
			orderBy='SetInfo.ReleaseYear, SetInfo.ReleaseMonth'
		})
	for r = 1, #vars.cardsets do
		local result = vars.cardsets[r]
		vars.categories[#vars.categories+1] = set_category[result['SetData.SetName']]
	end
	vars.shortset_from_name = function(self)
		return shortset(self['SetData.SetName'])
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
	local card_results = cargo_results(
		'CardData',
		'Name,Image,Artist,Text,FlavorText,Type,Rarity,House,Traits,Power,Armor,Amber',
        {
			where='CardData.Name="'..frame.args.cardname..'"'
		})
	if(frame.args.locale) then
		load_translation_table(frame.args.locale)
	end
	vars.cardname_e = vars.cardname
	vars.word_power = 'Power'
	vars.word_armor = 'Armor'
	vars.word_artist = 'Artist'
    vars.cardimage = card_results[1]['Image']
	vars.cardhouse = card_results[1]['House']
	vars.cardhouse_lower = vars.cardhouse:lower()
	vars.cardrarity = card_results[1]['Rarity']
	vars.cardtext = wikitext(card_results[1]['Text'])
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
		vars.locale = frame.args.locale
		vars.locales = {}
		vars.locales[1] = {keyforge="pt-pt", locale="/locale/pt-br", locale_name="português do Brasil"}
		vars.locales[2] = {keyforge="it-it", locale="/locale/it", locale_name="italiano"}
		vars.locales[3] = {keyforge="zh-hant", locale="/locale/zh-hant", locale_name="中文（繁體）"}
		vars.locales[4] = {keyforge="de-de", locale="/locale/de", locale_name="Deutsch"}
		vars.locales[5] = {keyforge="zh-hans", locale="/locale/zh", locale_name="中文"}
		vars.locales[6] = {keyforge="th-th", locale="/locale/th", locale_name="ไทย"}
		vars.locales[7] = {keyforge="ko-ko", locale="/locale/ko", locale_name="한국어"}
		vars.locales[8] = {keyforge="pl-pl", locale="/locale/pl", locale_name="polski"}
		vars.locales[9] = {keyforge="fr-fr", locale="/locale/fr", locale_name="français"}
		vars.locales[10] = {keyforge="es-es", locale="/locale/es", locale_name="español"}
		vars.locales[11] = {keyforge="en-en", locale="", locale_name="english"}
		local locale_table_results = cargo_results(
			'CardLocaleData',
			'Name,EnglishName,Text,FlavorText,Locale,Image',
			{
				where='CardLocaleData.EnglishName="'..frame.args.cardname..'" and CardLocaleData.Locale="'..frame.args.locale..'"'
			}
		)
		for c = 1, #locale_table_results do
			local cardlocale = locale_table_results[c]
			vars.cardtext = wikitext(cardlocale['Text'])
			vars.cardname = cardlocale['Name']
			vars.cardflavortext = wikitext(cardlocale['FlavorText'])
			vars.cardimage = cardlocale['Image']
		end
	end
    
	apply_sets(frame, vars)
	apply_altart(frame, vars)
	apply_house(frame, vars)
	apply_stats(frame, vars)
	apply_traits(frame, vars)
	apply_errata(frame, vars)
	apply_rulings(frame, vars)

	if not frame.args.locale then
		apply_categories(frame, vars)
	else
		vars.categories = ''
	end

	text = stache(templates.template_base, vars):gsub('\n','')
	text = frame:preprocess(text)
	text = dewikitext(text)
	return text
end

return p
