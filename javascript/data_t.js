var set_numbers = [
	[452, "Worlds Collide"],
	[453, "Worlds Collide"], //Anomalys
	[341, "Call of the Archons"],
	[435, "Age of Ascension"],
	[479, "Mass Mutation"],
	[496, "Dark Tidings"],
	[600, "Winds of Exchange"],
	[601, "Unchained"],
	[609, "Vault Masters 2023"],
	[700, "Grim Reminders"],
	[722, "Menagerie 2024"],
	[990, "Æmber Skies"],
	[991, "Vault Masters 2024"],
	[992, "Tokens of CHange"]
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
		if(setname !== 'Exclude Reprints') {
			houses_by_set[setname].forEach((h)=>{
				s.add(h)
			})
		}
	})
	return Array.from(s).sort()
}
var getDeckHouses = function(set_filter) {
	return getHouses(set_filter).filter(function(house) {
		return house !== 'Anomaly'
	})
}

var orders = {"Name":"Name","House":"House","Number":"CardNumber","Rarity":"Rarity","Power":"Power","Recently Added":"CardData._rowID DESC"}

var multiHouseCards = ["It’s Coming...", "Dark Æmber Vault"]

var images = {
	enhanceAmber: 'https://archonarcana.com/images/f/fb/Enhance_aember.png',
	enhanceCapture: 'https://archonarcana.com/images/f/fc/Enhance_capture.png',
	enhanceDamage: 'https://archonarcana.com/images/5/50/Enhance_damage.png',
	enhanceDraw: 'https://archonarcana.com/images/a/ac/Enhance_draw.png',
	enhanceDiscard: 'https://archonarcana.com/images/4/41/Enhance_discard.png',

	raritySpecial: 'https://archonarcana.com/images/thumb/3/34/Rarity-special.png/25px-Rarity-special.png',
	rarityCommon: 'https://archonarcana.com/images/thumb/e/e4/Rarity-common.png/25px-Rarity-common.png',
	rarityUncommon: 'https://archonarcana.com/images/thumb/d/d3/Rarity-uncommon.png/25px-Rarity-uncommon.png',
	rarityRare: 'https://archonarcana.com/images/thumb/c/c2/Rarity-rare.png/25px-Rarity-rare.png',
	rarityEviltwin: 'https://archonarcana.com/images/thumb/4/42/Evil-twin.png/25px-Evil-twin.png' 
}

//CARDCOMBOS

function getSet(setname, metadata) {
	for(let i=0;i<metadata.cardsets.length;i++) {
		let found_set = metadata.cardsets[i]
		let found_setname = found_set['SetInfo.SetName'].replaceAll(' ', '_')
		if(found_setname == setname) {
			if(!found_set['Houses']) {
				found_set['Houses'] = {}
			}
			return found_set
		}
	}
	return {'Houses': {}}
}
  
function number_range(text_input) {
	let ret = {"min":"", "max":""}
	if(text_input.includes("-")){
		var spl = text_input.split("-",2).map((t)=>t.trim())
		if(spl.length<2) {
			ret["min"] = spl[0]
			ret["max"] = spl[0]
		} else {
			ret["min"] = spl[0]
			ret["max"] = spl[1]
		}
	} else if (text_input.includes("+")) {
		var spl = text_input.split("+",1).map((t)=>t.trim())
		ret["min"] = spl[0]
	} else {
		ret["min"] = text_input.trim()
		ret["max"] = text_input.trim()
	}
	ret["min"] = (parseInt(ret["min"])).toString()
	ret["max"] = (parseInt(ret["max"])).toString()
	if(ret["min"]=="NaN") {ret["min"]=""}
	if(ret["max"]=="NaN") {ret["max"]=""}
	return ret
}

function getDistinctFieldFromMetadata(set_filter, field, underscores, metadata){
	var s = new Set()
	set_filter.map((setname)=>{
		if(setname !== 'Exclude Reprints') {
			Object.keys(getSet(setname, metadata)[field]).forEach((val)=>{
				if(underscores) {
					val = val.replaceAll(" ", "_")
				}
				s.add(val)
			})
		}
	})
	return Array.from(s).sort()
}

function getHousesFromMetadata(set_filter, metadata){
	return getDistinctFieldFromMetadata(set_filter, 'Houses', true, metadata)
}

function getArtistsFromMetadata(set_filter, metadata){
	return getDistinctFieldFromMetadata(set_filter, 'Artists', false, metadata)
}

function getTraitsFromMetadata(set_filter, metadata){
	return getDistinctFieldFromMetadata(set_filter, 'Traits', false, metadata)
}

function getTypesFromMetadata(set_filter, metadata){
	return getDistinctFieldFromMetadata(set_filter, 'Types', false, metadata)
}

function getRaritiesFromMetadata(set_filter, metadata){
	return getDistinctFieldFromMetadata(set_filter, 'Rarities', false, metadata)
}

function getKeywordsFromMetadata(set_filter, metadata){
	return getDistinctFieldFromMetadata(set_filter, 'Keywords', false, metadata)
}

export {
	multiHouseCards,
	orders, getHouses, getDeckHouses,
	cardCombos, images, set_name_by_number, set_number_by_name,
	number_range,
	getDistinctFieldFromMetadata, getHousesFromMetadata, getArtistsFromMetadata, getTraitsFromMetadata,
	getTypesFromMetadata, getRaritiesFromMetadata, getKeywordsFromMetadata
}
