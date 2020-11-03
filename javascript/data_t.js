var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation']
var spoiler_sets = ['Dark_Tidings']
var houses_by_set = {
	'Call_of_the_Archons': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Age_of_Ascension': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Worlds_Collide': new Set(['Dis','Logos','Saurian','Star_Alliance','Shadows','Untamed','Anomaly', 'Brobnar']),
	'Mass_Mutation': new Set(['Dis','Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed']),
	'Dark_Tidings': new Set(['Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed', 'Unfathomable'])
}
var set_numbers = [
	[452, "Worlds Collide"],
	[453, "Worlds Collide"],
	[341, "Call of the Archons"],
	[435, "Age of Ascension"],
	[479, "Mass Mutation"]
]
var set_name_by_number = function(number) {
	return set_numbers.filter(function(set){
		return set[0] == number
	})[0][1]
}
var set_number_by_name = function(name) {
	return set_numbers.filter(function(set){
		return set[1].toLowerCase() === name.replace(/\_/g, ' ').toLowerCase()
	})[0][0]
}
var getHouses = function(set_filter){
	var s = new Set()
	set_filter.map((setname)=>{
		houses_by_set[setname].forEach((h)=>{
			s.add(h)
		})
	})
	return Array.from(s).sort()
}
var ambercounts = ['0', '1', '2', '3', '4+']
var armorcounts = ['0', '1', '2', '3', '4', '5+']
var powercounts = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10+']
var enhancecounts = ['1', '2', '3', '4', '5+']
var houses = getHouses(sets)
var spoilerhouses = getHouses(spoiler_sets)

var types = ['Creature', 'Artifact', 'Upgrade', 'Action']
var rarities = ['Common', 'Uncommon', 'Rare', 'Fixed', 'Variant', 'Special']
var set5rarities = ['Common', 'Uncommon', 'Rare', 'Fixed', 'Variant', 'Special', 'Evil Twin']
var orders = {"Name":"Name","House":"House","Number":"CardNumber","Rarity":"Rarity","Power":"Power"}
var keywords = ['Alpha',
  'Assault',
  'Deploy',
  'Elusive',
  'Hazardous',
  'Invulnerable',
  'Omega',
  'Poison',
  'Skirmish',
  'Taunt']
var features = ['gigantic', 'errata']

var images = {
	enhanceAmber: 'https://archonarcana.com/images/f/fb/Enhance_aember.png',
	enhanceCapture: 'https://archonarcana.com/images/f/fc/Enhance_capture.png',
	enhanceDamage: 'https://archonarcana.com/images/5/50/Enhance_damage.png',
	enhanceDraw: 'https://archonarcana.com/images/a/ac/Enhance_draw.png',

	raritySpecial: 'https://archonarcana.com/images/thumb/3/34/Rarity-special.png/25px-Rarity-special.png',
	rarityCommon: 'https://archonarcana.com/images/thumb/e/e4/Rarity-common.png/25px-Rarity-common.png',
	rarityUncommon: 'https://archonarcana.com/images/thumb/d/d3/Rarity-uncommon.png/25px-Rarity-uncommon.png',
	rarityRare: 'https://archonarcana.com/images/thumb/c/c2/Rarity-rare.png/25px-Rarity-rare.png',
	rarityEviltwin: 'https://archonarcana.com/images/thumb/4/42/Evil-twin.png/25px-Evil-twin.png' 
}

//ARTISTS
//SET5ARTISTS
//TRAITS
//SET5TRAITS
//CARDCOMBOS

export {artists, set5artists, traits, set5traits, sets, houses, spoiler_sets,
		ambercounts, armorcounts, powercounts, enhancecounts, spoilerhouses, 
		types, rarities, set5rarities, orders, keywords, features, getHouses,
		cardCombos, images, set_name_by_number, set_number_by_name
	}