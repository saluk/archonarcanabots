--Module:LuacardKFA
--canstage
--Usage: english - {{#invoke luacard | viewcard | cardname=Angry Mob}} 
--       other language {{#invoke luacard | viewcard | cardname=Angry Mob | locale=fr-fr}}   (language codes are all 2 part)
--Debug: print(p.viewcard({args={cardname='Angry Mob', debug=true}}))
local p = {}
local cargo = mw.ext.cargo

function combine(tableto, tablefrom)
	for k,v in pairs(tablefrom) do
		tableto[k] = v
	end
end

function map(table, func)
	if table==nil then return table end
	for k,v in pairs(table) do
		table[k] = func(v)
	end
	return table
end

function filter(table, func)
	if table==nil then return table end
	local new = {}
	for k,v in pairs(table) do
		if func(v) then new[k] = v
		end
	end
	return new
end

function append(table, value)
	table[#table+1] = value
	return table
end

function extend(table1, table2)
	for k,v in pairs(table2) do
		append(table1, v)
	end
end

local templates = require('Module:LuacardTemplates')
local cardstyle = require('Module:LuacardStyle')
local translations = require("Module:LocaleTable") -- double quotes to not stage
local luastache = require("Module:luastache")  -- double quotes to not stage

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
		if v==nil then
			table[k] = ''
			v = ''
		end
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
	stachify(tab)
	insert_translated(tab)
	s = '{{=${ }=}}'..s
	return luastache:render(s, tab)
end

function wikitext(s)
	if s==nil then
		return ''
	else
		return s:gsub('\n', ''):gsub('<p>','__PARA__')
	end
end

function dewikitext(s)
	if s==nil then
		return ''
	end
	return s:gsub('__PARA__', '<p>')
end

local set_category = {}
set_category['Call of the Archons']='CotA'
set_category['Age of Ascension']='AoA'
set_category['Worlds Collide']='WC'
set_category['Mass Mutation']='MM'
set_category['Dark Tidings']='DT'

local translate_trait = function(frame, type, word)
	if(frame.args.locale) then
		if(not translations[type][frame.args.locale]) then
			return word
		end
		if(not translations[type][frame.args.locale][mw.ustring.lower(word)]) then
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
	if frame.args.locale then
		vars.art_default = true
		return
	end
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
	if vars.cardhouse ~= nil then
		vars.is_multi = string.find(vars.cardhouse, '•', 1, true)
		vars.is_anomaly = string.find(vars.cardhouse, 'Anomaly')
		vars.is_starAlliance = string.find(vars.cardhouse, 'Star Alliance')
	end
	if(vars.is_multi) then
		vars.cardhouse_color = ''
		append(vars.categories, 'Multi')
	else
		vars.cardhouse_color = mw.ustring.gsub(vars.cardhouse, '%s', '')
		vars.cardhouse_color = mw.ustring.sub(vars.cardhouse_color, 1, 1):lower() .. mw.ustring.sub(vars.cardhouse_color, 2)
		append(vars.categories, vars.cardhouse)
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
	if vars.cardtraits==nil then
		return
	end
	if(string.len(mw.text.trim(vars.cardtraits))==0) then
		return
	end
	local split = mw.text.split(vars.cardtraits, ' • ')
	vars.cardtraits = {}
	vars.translate_trait = function(self)
		return translate_trait(frame, 'traits', self.trait)
	end
	for i = 1, #split do
		append(vars.categories, split[i])
		local ob = {}
		ob.trait = split[i]
		if i<#split then
			ob.delim = true
		end
		append(vars.cardtraits, ob)
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
		vars.original_text=errata_results[1]['ErrataData.Text']
		vars.errata_text=errata_results[#errata_results]['ErrataData.Text']
		vars.errata_version = errata_results[#errata_results]['ErrataData.Version']
		if(string.find(vars.errata_version, 'Rulebook')) then
			append(vars.categories, 'Errata')
		else
			append(vars.categories, 'Revised Cards')
		end
	end
end

function apply_categories(frame, vars)
	mw.log(vars.category_prefix)
	for c=1, #vars.categories do
		if(string.len(mw.text.trim(vars.categories[c]))>0) then
			vars.categories[c] = vars.category_prefix .. vars.categories[c]
			vars.categories[c] = stache('[[Category:${c}]]', {c=vars.categories[c]})
		end
	end
	mw.logObject(vars.categories)
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
	if(#official_results>0) then append(vars.categories, 'FAQ') end

	local ruling_results = rulequery('FFGRuling', vars.cardname_e)
	if(#ruling_results>0) then append(vars.categories, 'FFG Rulings') end

	extend(official_results, ruling_results)

	local commentary_results = rulequery('Commentary', vars.cardname_e)
	local outstanding_results = rulequery('OutstandingIssues', vars.cardname_e)

	vars.ruleofficial = official_results
	mw.logObject(ruleofficial)
	vars.has_ruleofficial = #vars.ruleofficial > 0
	vars.rulecommentary = commentary_results
	vars.has_rulecommentary = #vars.rulecommentary > 0
	vars.ruleoutstanding = filter(outstanding_results, function(ruling)
		if string.find(ruling['RulesText'], '//') then 
			return true 
		else return false 
		end
	end)
	vars.has_ruleoutstanding = #vars.ruleoutstanding > 0

	if(has_ruleoutstanding or has_rulecommentary) then append(vars.categories, 'Commentary') end

	vars.filter_rules_text = function(self)
		return self['RulesText']:gsub('this card', "'''"..vars.cardname_e.."'''")
	end
end

function relatedquery(cardname)
	return cargo_results(
		'CardRelatedData',
		'Pages, Text, Cards, Type',
		{
			groupBy='Pages, Text, Cards, Type',
			where="(Pages like '%•"..cardname.."•%' OR (pages IS null AND Cards like '%•"..cardname.."•%')) AND Type!='Twin'",
			orderBy='Text ASC'
		})
end

function relatedflavorquery(cardname)
    return cargo_results(
        'CardData',
        'Name, FlavorText',
        {
            where="(CardData.FlavorText LIKE '%"..cardname.."%') AND (CardData.Name NOT LIKE '%"..cardname.."%')",
            orderBy='CardData.Name ASC'
        })
end

function twinquery(cardname)
	local searchname = cardname
	if string.find(cardname, 'Evil Twin') ~= nil then
		searchname = cardname:gsub(' %(Evil Twin%)', ' ')
		mw.log('search for not evil twin '..searchname)
	else
		searchname = cardname..' (Evil Twin)'
		mw.log('search for the evil twin '..searchname)
	end
	return cargo_results(
		'CardData',
		'Name',
		{
			groupBy='Name',
			where='Name="'..searchname..'"'
		})
end

function get_related_cards(cardname, related_row)
	local cards = {}
	local card_names = related_row['Cards']
	if card_names==nil then return cards end
	for name, _ in mw.ustring.gmatch(card_names, '[^•]+') do
		mw.log(name..', '..cardname)
		if name~=cardname then
			local card_results = cargo_results(
				'CardData',
				'Name,Image,Artist,Text,FlavorText,Type,Rarity,House,Traits,Power,Armor,Amber',
				{
					where='CardData.Name="'..name..'"'
				})
			if card_results[1] ~= nil then
				card_results[1]["Name_br"] = mw.ustring.gsub(card_results[1]["Name"], "%(", "<br>(")
			end
			append(cards, card_results[1])
		end
	end
	return cards
end

function apply_related(frame, vars)
	-- we use cardname_e and just show english related
	local related_set = {}
	local related_cards_set = relatedquery(vars.cardname_e)
	local related_flavor_set = relatedflavorquery(vars.cardname_e)
	local related_twin_set = twinquery(vars.cardname_e)
	mw.logObject(related_twin_set)
	map(related_twin_set, function(item)
		local twin_name = 'an Evil Twin'
		if item["Name"]:find('Evil Twin')==nil then twin_name = 'a non-Evil Twin' end
		append(related_set, {
			Pages = "•"..vars.cardname_e.."•",
			Text = "this card has "..twin_name.." version:",
			Cards = "•"..item["Name"].."•"
		})
	end)
	if #related_flavor_set > 0 then
		local flavor_card_names = ""
		for i=1, #related_flavor_set do
			flavor_card_names = flavor_card_names .. "•"..related_flavor_set[i]["Name"].."•"
		end
		append(related_set, {
			Pages = "•"..vars.cardname_e.."•",
			Text = "this card is featured in the flavor text of the following cards:",
			Cards = flavor_card_names
		})
	end
	extend(related_set, related_cards_set)
	map(related_set, function(item)
		item['Text'] = item['Text']:gsub('this card', "'''"..vars.cardname_e.."'''")
		item['Cards'] = get_related_cards(frame.args.cardname, item)
		return item
	end)
	vars.related = {}
	vars.cardnotes = {}
	for _,row in pairs(related_set) do
		mw.log(row)
		if #row['Cards']>0 then
			append(vars.related, row)
			mw.log('have related')
		else
			append(vars.cardnotes, row)
			mw.log('have notes')
		end
	end
	if(#vars.related>0) then vars.has_related = true end
	if(#vars.cardnotes>0) then vars.has_notes = true end
end

function apply_sets(frame, vars)
	vars.cardsets = cargo_results(
		'SetData,CardData,SetInfo',
		'SetData.SetName, SetData.CardNumber, SetInfo.ReleaseYear, SetInfo.ReleaseMonth, SetInfo.ShortName, SetInfo.SetNumber',
		{
			join='SetData._pageTitle=CardData.Name,SetData.SetName=SetInfo.SetName',
			where='CardData.Name="'..frame.args.cardname..'"',
			orderBy='SetInfo.ReleaseYear, SetInfo.ReleaseMonth'
		})
	for r = 1, #vars.cardsets do
		local result = vars.cardsets[r]
		mw.log(result['SetInfo.SetNumber'])
		if mw.ustring.find(result['SetInfo.SetNumber'], 'KFA.*') ~= nil then
			vars.category_prefix = 'KFA '
		end
		mw.log(vars.category_prefix)
		append(vars.categories, set_category[result['SetData.SetName']])
	end
	vars.shortset_from_name = function(self)
		local args = {longset = self['SetData.SetName'], shortset=self['SetInfo.ShortName']}
		return stache('[[${longset}|${shortset_t}]]', args)
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
	vars.cardname_stripped = mw.ustring.gsub(vars.cardname_e, " %(Evil Twin%)", "")
	vars.cardname_stripped = mw.ustring.gsub(vars.cardname_stripped, " %(Anomaly%)", "")
	vars.word_power = 'Power'
	vars.word_armor = 'Armor'
	vars.word_artist = 'Artist'
    vars.cardimage = card_results[1]['Image']
	vars.cardhouse = card_results[1]['House']
	vars.cardrarity = card_results[1]['Rarity']
	vars.cardtext = wikitext(card_results[1]['Text'])
	vars.cardflavortext = wikitext(card_results[1]['FlavorText'])
	vars.cardartist = card_results[1]['Artist'] or ''
	vars.cardtype = card_results[1]['Type']
	vars.cardpower = card_results[1]['Power'] or '0'
	vars.cardarmor = card_results[1]['Armor'] or '0'
	vars.cardamber = card_results[1]['Amber'] or '0'
	vars.cardtraits = card_results[1]['Traits'] or ''
	vars.category_prefix = ''
	if vars.cardhouse == nil then 
		vars.cardhouse = ''
		vars.has_no_house = true
	end
	if vars.cardtype == nil then vars.cardtype = '' end
	if vars.cardrarity == nil then 
		vars.cardrarity = ''
		vars.has_no_rarity = true
	end
	vars.categories = {vars.cardtype, vars.cardrarity, 'Card'}
	if(string.find(vars.cardtext,vars.cardname_stripped)) then
		append(vars.categories, 'Self-referential')
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
		vars.locales[12] = {keyforge="ru-ru", locale="/locale/ru", locale_name="Pусский"}
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
	apply_related(frame, vars)

	if not frame.args.locale then
		apply_categories(frame, vars)
	else
		vars.categories = ''
	end

	text = stache(templates.template_base:gsub('\n',''), vars)
	if(frame.args.debug==nil) then
		text = frame:preprocess(text)
	end
	text = dewikitext(text)
	return text
end

return p
