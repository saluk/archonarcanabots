--Module:Luacard
local p = {}
local cargo = mw.ext.cargo

local templates = mw.loadData('Module:LuacardTemplates')
local cardstyle = mw.loadData('Module:LuacardStyle')

function interp(s, tab)
  return (s:gsub('($%b{})', function(w) return tab[w:sub(3, -2)] or w end))
end

local join = function ( separator, array )
    return table.concat( array, separator, 1, #array )
end

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
    vars.cardimage = card_results[1]['Image']
	vars.cardhouse = card_results[1]['House']
	vars.cardhouse_lower = vars.cardhouse:lower()
	vars.cardrarity = card_results[1]['Rarity']
	vars.cardtext = card_results[1]['Text']
	vars.cardartist = card_results[1]['Artist']
	vars.cardtype = card_results[1]['Type']
    
	local set_number_results = cargo.query(
		'SetData,CardData,SetInfo',
		'SetData.SetName, SetData.CardNumber, SetInfo.ReleaseYear, SetInfo.ReleaseMonth',
		{
			join='SetData._pageTitle=CardData.Name,SetData.SetName=SetInfo.SetName',
			where='CardData.Name="'..frame.args.cardname..'"',
			orderBy='SetInfo.ReleaseYear, SetInfo.ReleaseMonth'
		})
	local cardnumber_short = {}
	for r = 1, #set_number_results do
		local result = set_number_results[r]
		cardnumber_short[r] = ''..shortset(result['SetData.SetName'])..':'..result['SetData.CardNumber']
	end
    vars.cardnumber_short = join(',&nbsp;', cardnumber_short)
	
	apply_altart(frame, vars)

	if(vars.cardhouse:find('•', 1, true)) then
		vars.cardhouse_section = 'Multi'
	else
		if(vars.cardhouse:find('Anomaly')) then
			vars.cardhouse_section = '{{House|House=Anomaly|Size=20px}} <html><a href="https://archonarcana.com/Card_Gallery?houses=Anomaly">Anomaly</a></html>'
		else
			vars.cardhouse_section = '{{House|House=${cardhouse}|Size=25px}} [[Houses#${cardhouse}|${cardhouse}]]'
		end
	end
	vars.cardhouse_section = interp(vars.cardhouse_section, vars)

	text = frame:preprocess(interp(templates.template_base, vars))
	return text
end

return p
