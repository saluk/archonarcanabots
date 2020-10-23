var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation']
var spoiler_sets = ['Dark_Tidings']
var houses_by_set = {
	'Call_of_the_Archons': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Age_of_Ascension': new Set(['Brobnar','Dis','Logos','Mars','Sanctum','Shadows','Untamed']),
	'Worlds_Collide': new Set(['Dis','Logos','Saurian','Star_Alliance','Shadows','Untamed','Anomaly', 'Brobnar']),
	'Mass_Mutation': new Set(['Dis','Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed']),
	'Dark_Tidings': new Set(['Logos','Sanctum','Saurian','Star_Alliance','Shadows','Untamed', 'Unfathomable'])
}
var set_name_by_number = function(number) {
	return {
        452: "Worlds Collide",
        453: "Worlds Collide",
        341: "Call of the Archons",
        435: "Age of Ascension",
        479: "Mass Mutation"
	}[number]
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

var artists = ['Adam Schumpert', 'Adam Vehige', 'Agri Karuniawan', 'Albert Bruun', 'Alena Medovnikova', 'Alena Zhukova', 'Alexandre Leoni', 'Alexey Iavtuschenco', 'Allon Kremer', 'Alyn Spiller', 'Ameen Naksewee', 'Andreas Zafiratos', 'Andrew Bosley', 'Angelica Alieva', 'Angelina Chernyak', 'Anton Zemskov', 'Anzka Nguyen', 'Art tavern', 'Asep Ariyanto', 'Atha Kanaani', 'BalanceSheet', 'Bogdan Tauciuc', 'Brandon Hunt', 'Brolken', 'Caio Monteiro', 'Caravan Studio', 'Chris Bjors', 'Cindy Avelino', 'Colin Searle', 'Dany Orizio', 'David Auden Nash', 'David Keen', 'David Kegg', 'David Pursley', 'David Tenorio', 'Diego Machuca', 'Djib', 'Dong Cheng', 'Eric Kenji Aoyagi', 'Etienne Hebinger', 'Felipe Martini', 'Forrest Imel', 'Francisco Badilla', 'Fábio Perez', 'Gabriel Rubio', 'Gabriel Scavariello', 'Gabriel Zanini', 'Gabriela Marchioro', 'Girma Moges', 'Gizelle Karen Baluso', 'Gong Studios', 'Grigory Serov', 'Hans Krill', 'Harumi Namba', 'Helena Butenkova', 'Hendry Iwanaga', 'Ilya Bondarenko', 'Iqnatius Budi', 'Ivan Frolov', 'Ivan Tao', 'JB Casacop', 'Jacob Atienza', 'Jacob Walker', 'Jacqui Davis', 'Jason Juta', 'Jessada Sutthi', 'Jessé Suursoo', 'John Silva', 'Jon Bosco', 'Jordan Kerbow', 'Jorge Ramos', 'Josh Corpuz', 'Konstantin Porubov', 'Konstantin Turovec', 'Kristen Pauline', 'Kristina Kolesnikova', 'Leandro Franci', 'Liiga Smilshkalne', 'Limetown Studios', 'Lorena Lammer', 'Mads Ahm', 'Maerel Hibadita', 'Marc Escachx', 'Marco Tamura', 'Maria Poliakova', 'Mariana Ennes', 'Mariusz Gandzel', 'Mark Bulahao', 'Marko Fiedler', 'Marzena Piwowar', 'Matheus Schwartz', 'Matt Zeilinger', 'Matthew Mizak', 'Melvin Chan', 'Michele Giorgi', 'Mihai Radu', 'Mircea Nicula', 'Mo Mukhtar', 'Monztre', 'Nasrul Hakim', 'Natalie Russo', 'Nicholas Gregory', 'Nicola Saviori', 'Oscar Römer', 'Pavel Tomashevskiy', 'Pedro Dutra', 'Preston Stone', 'Quentin de Warren', 'Radial Studio', 'Randall Mackey', 'Raphael Massarani', 'Regis Torres', 'Rodrigo Camilo', 'Roman Semenenko', 'Ronnie Price II', 'Rudy Siswanto', 'Sasha Tudvaseva', 'Sean Donaldson', 'Stanislav Dikolenko', 'Taylor Ingvarsson', 'Tey Bartolome', 'Timur Shevtsov', 'Tomek Larek', 'Vladimir Kafanov', 'Vladimir Zyrianov', 'Yan Kyohara', 'Ângelo Bortolini']
var set5artists = ['Alexandre Leoni', 'Art Tavern', 'BalanceSheet', 'Bogdan Tauciuc', 'Brian Fajardo', 'Brolken', 'Caio Monteiro', 'Chris Bjors', 'David Tenorio', 'Dong Cheng', 'Gabriel Rubio', 'John Silva', 'Marc Escachx', 'Mariana Ennes', 'Michele Giorgi', 'Monztre', 'Radial Studio', 'Radial Studios', 'Roman Semenenko', 'Stanislav Dikolenko', 'Tomek Larek', 'Vladimir Kafanov', 'Vladimir Zyrianov', 'Ângelo Bortolini']
var traits = ['AI', 'Agent', 'Alien', 'Ally', 'Angel', 'Aquan', 'Assassin', 'Beast', 'Cat', 'Changeling', 'Cyborg', 'Demon', 'Dinosaur', 'Dragon', 'Egg', 'Elf', 'Equation', 'Experiment', 'Faerie', 'Fungus', 'Giant', 'Goblin', 'Handuhan', 'Horseman', 'Human', 'Hunter', 'Imp', 'Insect', 'Item', 'Jelly', 'Knight', 'Krxix', 'Law', 'Leader', 'Location', 'Martian', 'Merchant', 'Monk', 'Mutant', 'Niffle', 'Philosopher', 'Pilot', 'Pirate', 'Politician', 'Power', 'Priest', 'Proximan', 'Psion', 'Quest', 'Ranger', 'Rat', 'Redacted', 'Robot', 'Scientist', 'Shapeshifter', 'Shard', 'Sin', 'Soldier', 'Specter', 'Spirit', 'Thief', 'Tree', 'Vehicle', 'Weapon', 'Witch', 'Wolf']
var set5traits = ['AI', 'Alien', 'Angel', 'Aquan', 'Beast', 'Dinosaur', 'Elf', 'Fisher', 'Human', 'Knight', 'Mutant', 'Politician', 'Power', 'Robot', 'Scientist', 'Ship', 'Spirit', 'Thief', 'Witch']
var cardCombos = [['Binate Rupture', 'Interdimensional Graft'], ['Drummernaut', 'Ganger Chieftain'], ['Tribute', 'Exile'], ['Tribute', 'Sic Semper Tyrannosaurus'], ['Cincinnatus Rex', 'The Golden Spiral'], ['Livia the Elder', 'Legatus Raptor'], ['Livia the Elder', 'Cincinnatus Rex'], ['Mega Narp', 'The Flex'], ['Duskwitch', 'Skybooster Squadron'], ['Song of the Wild', 'Ghosthawk'], ['Commpod', 'Crystal Hive'], ['Combat Pheromones', 'Crystal Hive'], ['The Sting', 'Whispering Reliquary'], ['The Sting', 'Snudge'], ['The Sting', 'Vezyma Thinkdrone'], ['Hysteria', 'A Fair Game'], ['Loot the Bodies', 'Coward’s End'], ['Hecatomb', 'Arise!'], ['Control the Weak', 'A Fair Game'], ['Library Card', 'Dark Æmber Vault'], ['Auto-Encoder', 'Punctuated Equilibrium'], ['Library Access', 'Reverse Time'], ['Helmsman Spears', 'Stealth Mode'], ['Com. Officer Kirby', 'Punctuated Equilibrium'], ['Replicator', 'Professor Sutterkin'], ['Hysteria', 'Lesser Oxtet'], ['Bouncing Deathquark', 'Archimedes'], ['Neutron Shark', 'Self-Bolstering Automata'], ['Neutron Shark', 'Reassembling Automaton'], ['General Order 24', 'Self-Bolstering Automata'], ['General Order 24', 'Reassembling Automaton'], ['Curia Saurus', 'Amphora Captura'], ['They’re Everywhere!', 'Save the Pack'], ['Scrivener Favian', 'Amphora Captura'], ['Reassembling Automaton', 'Discombobulator'], ['Reassembling Automaton', 'Quadracorder'], ['Kompsos Haruspex', 'Ronnie Wristclocks'], ['Kompsos Haruspex', 'Infurnace'], ['Control the Weak', 'Dominator Bauble', 'Witch of the Eye'], ['Control the Weak', 'Deipno Spymaster', 'Witch of the Eye'], ['Control the Weak', 'Screaming Cave'], ['Ronnie Wristclocks', 'Too Much to Protect', 'Nerve Blast'], ['Fandangle', 'Snudge'], ['Duskwitch', 'Snudge'], ['Screaming Cave', 'Infurnace'], ['Infurnace', 'Universal Recycle Bin'], ['Miasma', 'Too Much to Protect'], ['Rad Penny', 'Seeker Needle'], ['Safe House', 'Bo Nithing'], ['Potion of Invulnerability', 'The Grey Rider'], ['Into the Fray', 'Potion of Invulnerability'], ['Infurnace', 'Snudge'], ['Martian Generosity', 'Key Abduction'], ['Battle Fleet', 'Key Abduction'], ['Heart of the Forest', 'Grasping Vines', 'Chota Hazri'], ['Heart of the Forest', 'Grasping Vines', 'Key Charge'], ['The Sting', 'Key Charge'], ['The Sting', 'Chota Hazri']]

export {artists, set5artists, traits, set5traits, sets, houses, spoiler_sets,
		ambercounts, armorcounts, powercounts, enhancecounts, spoilerhouses, 
		types, rarities, set5rarities, orders, keywords, features, getHouses,
		cardCombos, images, set_name_by_number
	}