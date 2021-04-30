var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation', 'Dark_Tidings']
var kfa_sets = ['Rise_of_the_Keyraken']
var spoiler_sets = ['Dark_Tidings']
var houses_by_set = {
	'Call_of_the_Archons': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Age_of_Ascension': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Worlds_Collide': new Set(['Dis','Logos','Saurian','Star_Alliance','Shadows','Untamed','Anomaly', 'Brobnar']),
	'Mass_Mutation': new Set(['Dis','Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed']),
	'Dark_Tidings': new Set(['Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed', 'Unfathomable']),
	'Rise_of_the_Keyraken': new Set(['Keyraken'])
}
var set_numbers = [
	[452, "Worlds Collide"],
	[453, "Worlds Collide"],
	[341, "Call of the Archons"],
	[435, "Age of Ascension"],
	[479, "Mass Mutation"],
	[496, "Dark Tidings"]   // TODO - for dark tidings update number
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
var getDeckHouses = function(set_filter) {
	return getHouses(set_filter).filter(function(house) {
		return house !== 'Anomaly'
	})
}
var ambercounts = ['0', '1', '2', '3', '4+']
var armorcounts = ['0', '1', '2', '3', '4', '5+']
var powercounts = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10+']
var enhancecounts = ['1', '2', '3', '4', '5+']
var houses = getHouses(sets)
var spoilerhouses = getHouses(spoiler_sets)

var types = ['Creature', 'Artifact', 'Upgrade', 'Action']
var rarities = ['Common', 'Uncommon', 'Rare', 'Fixed', 'Variant', 'Special', 'Evil Twin']
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

var multiHouseCards = ["It’s Coming...", "Dark Æmber Vault"]

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

var artists = ['Adam Schumpert', 'Adam Vehige', 'Agri Karuniawan', 'Albert Bruun', 'Alena Medovnikova', 'Alena Zhukova', 'Alexandre Leoni', 'Alexey Iavtuschenco', 'Allon Kremer', 'Alyn Spiller', 'Ameen Naksewee', 'Andreas Zafiratos', 'Andrew Bosley', 'Angelica Alieva', 'Angelina Chernyak', 'Anton Zemskov', 'Anzka Nguyen', 'Art Tavern', 'Asep Ariyanto', 'Atha Kanaani', 'BalanceSheet', 'Bogdan Tauciuc', 'Borja Pindado', 'Brandon Hunt', 'Brian Fajardo', 'Brolken', 'Caio Monteiro', 'Caravan Studio', 'Chris Bjors', 'Cindy Avelino', 'Colin Searle', 'Dany Orizio', 'David Auden Nash', 'David Keen', 'David Kegg', 'David Pursley', 'David Tenorio', 'Diego Gisbert', 'Diego Machuca', 'Djib', 'Dong Cheng', 'Edgar Hidalgo', 'Eric Kenji Aoyagi', 'Etienne Hebinger', 'Felipe Gonçalves', 'Felipe Martini', 'Flaviano Pivoto', 'Forrest Imel', 'Francisco Badilla', 'Fábio Perez', 'Gabriel Rubio', 'Gabriel Scavariello', 'Gabriel Zanini', 'Gabriela Marchioro', 'Girma Moges', 'Gizelle Karen Baluso', 'Gong Studios', 'Grigory Serov', 'Hans Krill', 'Harumi Namba', 'Helena Butenkova', 'Hendry Iwanaga', 'Ilya Bondarenko', 'Iqnatius Budi', 'Ivan Frolov', 'Ivan Tao', 'JB Casacop', 'Jacob Atienza', 'Jacob Walker', 'Jacqui Davis', 'Jason Juta', 'Jessada Sutthi', 'Jessé Suursoo', 'John Silva', 'Jon Bosco', 'Jordan Kerbow', 'Jorge Ramos', 'Josh Corpuz', 'Konstantin Porubov', 'Konstantin Turovec', 'Kristen Pauline', 'Kristina Kolesnikova', 'Leandro Franci', 'Leonardo Santanna', 'Liiga Smilshkalne', 'Limetown Studios', 'Lorena Lammer', 'Lucas Firmino', 'Mads Ahm', 'Maerel Hibadita', 'Marc Escachx', 'Marco Tamura', 'Maria Poliakova', 'Mariana Ennes', 'Mariusz Gandzel', 'Mark Bulahao', 'Marko Fiedler', 'Marzena Piwowar', 'Matheus Schwartz', 'Matt Zeilinger', 'Matthew Mizak', 'Melvin Chan', 'Michele Giorgi', 'Mihai Radu', 'Milica Čeliković', 'Mircea Nicula', 'Mo Mukhtar', 'Monztre', 'Nasrul Hakim', 'Natalie Russo', 'Nicholas Gregory', 'Nicola Saviori', 'Oscar Römer', 'Pavel Tomashevskiy', 'Pedro Dutra', 'Preston Stone', 'Quentin de Warren', 'Radial Studio', 'Randall Mackey', 'Raphael Massarani', 'Regis Torres', 'Rodrigo Camilo', 'Roman Semenenko', 'Ronnie Price II', 'Rudy Siswanto', 'Sasha Tudvaseva', 'Sean Donaldson', 'Sebastián Rodríguez', 'Stanislav Dikolenko', 'Steve Ellis', 'Taylor Ingvarsson', 'Tey Bartolome', 'Timur Shevtsov', 'Tomek Larek', 'Vladimir Kafanov', 'Vladimir Zyrianov', 'Yan Kyohara', 'Ângelo Bortolini']
var set5artists = ['Adam Schumpert', 'Adam Vehige', 'Alena Medovnikova', 'Alena Zhukova', 'Alexandre Leoni', 'Alexey Iavtushenco', 'Allon Kremer', 'Ameen Naksewee', 'Andreas Zafiratos', 'Andrew Bosley', 'Anzka Nguyen', 'Art tavern', 'Atha Kanaani', 'BalanceSheet', 'Bogdan Tauciuc', 'Borja Pindado', 'Brandon Hunt', 'Brian Fajardo', 'Brolken', 'Caio Monteiro', 'Caravan Studio', 'Chris Bjors', 'Cindy Avelino', 'Colin Searle', 'Dany Orizio', 'David Auden Nash', 'David Tenorio', 'Diego Gisbert', 'Diego Machuca', 'Djib', 'Dong Cheng', 'Edgar Hidalgo', 'Eric Kenji Aoyagi', 'Felipe Gonçalves', 'Felipe Martini', 'Flaviano Pivoto', 'Fábio Perez', 'Gabriel Rubio', 'Gabriel Scavariello', 'Gabriel Zanini', 'Gabriela Marchioro', 'Girma Moges', 'Gong Studios', 'Grigory Serov', 'Hans Krill', 'Helena Butenkova', 'Hendry Iwanaga', 'Ilya Bondarenko', 'Iqnatius Budi', 'Ivan Tao', 'JB Casacop', 'Jason Juta', 'Jessé Suursoo', 'John Silva', 'Jorge Ramos', 'Josh Corpuz', 'Konstantin Turovec', 'Kristina Kolesnikova', 'Leandro Franci', 'Leonardo Santanna', 'Liiga Smilshkalne', 'Lucas Firmino', 'Mads Ahm', 'Marc Escachx', 'Maria Poliakova', 'Mariana Ennes', 'Mark Bulahao', 'Marko Fiedler', 'Marzena Piwowar', 'Mateusz Mizak', 'Matheus Schwartz', 'Matthew Mizak', 'Michele Giorgi', 'Mihai Radu', 'Milica Čeliković', 'Mo Mukhtar', 'Monztre', 'Nasrul Hakim', 'Natalie Russo', 'Oscar Römer', 'Pedro Dutra', 'Quentin de Warren', 'Radial Studio', 'Regis Torres', 'Rodrigo Camilo', 'Roman Semenenko', 'Sean Donaldson', 'Sebastián Rodríguez', 'Stanislav Dikolenko', 'Steve Ellis', 'Timur Shevtsov', 'Tomek Larek', 'Vladimir Kafanov', 'Vladimir Zyrianov', 'Yan Kyohara', 'Ângelo Bortolini']
var kfa_artists = ['Alexandre Leoni', 'Borja Pindado', 'Brian Adriel', 'Chris Bjors', 'David Auden Nash', 'Ghais Ramadhani', 'Hans Krill', 'Ilham Zaka', 'Kevin Sidharta', 'Marc Escachx', 'Marko Fiedler', 'Monztre', 'Radial Studio', 'Tomek Larek', 'bimawithpencil']
var traits = ['AI', 'Agent', 'Alien', 'Ally', 'Angel', 'Aquan', 'Arm', 'Assassin', 'Beast', 'Cat', 'Changeling', 'Cyborg', 'Demon', 'Dinosaur', 'Dragon', 'Egg', 'Elf', 'Equation', 'Experiment', 'Faerie', 'Fisher', 'Fungus', 'Giant', 'Goblin', 'Handuhan', 'Horseman', 'Human', 'Hunter', 'Imp', 'Insect', 'Item', 'Jelly', 'Knight', 'Krxix', 'Law', 'Leader', 'Location', 'Martian', 'Merchant', 'Monk', 'Mutant', 'Niffle', 'Philosopher', 'Pilot', 'Pirate', 'Politician', 'Power', 'Priest', 'Proximan', 'Psion', 'Quest', 'Ranger', 'Rat', 'Redacted', 'Robot', 'Scientist', 'Shapeshifter', 'Shard', 'Ship', 'Sin', 'Soldier', 'Specter', 'Spirit', 'Thief', 'Treasure', 'Tree', 'Vehicle', 'Weapon', 'Witch', 'Wolf']
var set5traits = ['AI', 'Alien', 'Angel', 'Aquan', 'Beast', 'Cat', 'Cyborg', 'Dinosaur', 'Dragon', 'Elf', 'Fisher', 'Fungus', 'Handuhan', 'Human', 'Insect', 'Item', 'Knight', 'Krxix', 'Law', 'Leader', 'Location', 'Monk', 'Mutant', 'Philosopher', 'Pilot', 'Politician', 'Power', 'Priest', 'Proximan', 'Quest', 'Robot', 'Scientist', 'Ship', 'Soldier', 'Specter', 'Spirit', 'Thief', 'Treasure', 'Weapon', 'Witch']
var kfa_traits = ['Arm', 'Beast', 'Tentacle']
var cardCombos = []

export {artists, set5artists, kfa_artists, traits, set5traits, kfa_traits, sets, houses, spoiler_sets, kfa_sets,
		ambercounts, armorcounts, powercounts, enhancecounts, spoilerhouses, 
		multiHouseCards,
		types, rarities, set5rarities, orders, keywords, features, getHouses, getDeckHouses,
		cardCombos, images, set_name_by_number, set_number_by_name
	}