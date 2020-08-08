var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation']
var spoiler_sets = ['Dark_Tidings']
var houses_by_set = {
	'Call_of_the_Archons': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Age_of_Ascension': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Worlds_Collide': new Set(['Dis','Logos','Saurian','Star_Alliance','Shadows','Untamed','Anomaly']),
	'Mass_Mutation': new Set(['Dis','Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed']),
	'Dark_Tidings': new Set(['Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed', 'Unfathomable'])
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

var artists = ['Adam Schumpert', 'Adam Vehige', 'Agri Karuniawan', 'Albert Bruun', 'Alena Medovnikova', 'Alena Zhukova', 'Alexandre Leoni', 'Alexey Iavtuschenco', 'Allon Kremer', 'Alyn Spiller', 'Ameen Naksewee', 'Andreas Zafiratos', 'Andrew Bosley', 'Angelica Alieva', 'Angelina Chernyak', 'Anton Zemskov', 'Anzka Nguyen', 'Art tavern', 'Asep Ariyanto', 'Atha Kanaani', 'Ângelo Bortolini', 'BalanceSheet', 'Bogdan Tauciuc', 'Brandon Hunt', 'Brolken', 'Caio Monteiro', 'Caravan Studio', 'Chris Bjors', 'Cindy Avelino', 'Colin Searle', 'Dany Orizio', 'David Auden Nash', 'David Keen', 'David Kegg', 'David Pursley', 'David Tenorio', 'Diego Machuca', 'Djib', 'Dong Cheng', 'Eric Kenji Aoyagi', 'Etienne Hebinger', 'Fábio Perez', 'Felipe Martini', 'Forrest Imel', 'Francisco Badilla', 'Gabriel Rubio', 'Gabriel Scavariello', 'Gabriel Zanini', 'Gabriela Marchioro', 'Girma Moges']
var set5artists = ['Alexandre Leoni', 'Art Tavern', 'Ângelo Bortolini', 'BalanceSheet', 'Bogdan Tauciuc', 'Brian Fajardo', 'Brolken', 'Caio Monteiro', 'Chris Bjors', 'David Tenorio', 'Dong Cheng', 'John Silva', 'Marc Escachx', 'Mariana Ennes', 'Michele Giorgi', 'Monztre', 'Radial Studio', 'Radial Studios', 'Roman Semenenko', 'Stanislav Dikolenko', 'Tomek Larek', 'Vladimir Kafanov', 'Vladimir Zyrianov']
var traits = ['Agent', 'Martian', 'AI', 'Beast', 'Scientist', 'Alien', 'Handuhan', 'Human', 'Robot', 'Krxix', 'Proximan', 'Thief', 'Ally', 'Angel', 'Spirit', 'Aquan', 'Cat', 'Cyborg', 'Insect', 'Leader', 'Witch', 'Mutant', 'Niffle', 'Rat', 'Wolf', 'Pirate', 'Demon', 'Knight', 'Sin', 'Dinosaur', 'Assassin', 'Egg', 'Philosopher', 'Politician', 'Priest', 'Soldier', 'Dragon', 'Psion', 'Elf']
var set5traits = ['AI', 'Beast', 'Alien', 'Scientist', 'Angel', 'Aquan', 'Thief', 'Fisher', 'Witch', 'Dinosaur', 'Politician', 'Elf', 'Human', 'Knight', 'Mutant', 'Power', 'Robot', 'Ship', 'Spirit']
export {artists, set5artists, traits, set5traits, sets, houses, spoiler_sets,
		ambercounts, armorcounts, powercounts, enhancecounts, spoilerhouses, 
		types, rarities, set5rarities, orders, keywords, features, getHouses}