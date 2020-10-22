var houses = ['Brobnar','Dis','Logos','Mars','Sanctum','Saurian','Star_Alliance','Shadows','Untamed','Anomaly']
var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation']
var types = ['Creature', 'Artifact', 'Upgrade', 'Action']
var rarities = ['Common', 'Uncommon', 'Rare', 'Fixed', 'Variant']
var traits = ['AI', 'Agent', 'Alien', 'Ally', 'Angel', 'Aquan', 'Beast', 'Cyborg', 'Demon', 'Dinosaur', 'Dragon', 'Elf', 
              'Equation', 'Experiment', 'Faerie', 'Fungus', 'Giant', 'Goblin', 'Handuhan', 'Horseman', 'Human', 'Hunter', 
              'Imp', 'Insect', 'Item', 'Jelly', 'Knight', 'Krxix', 'Law', 'Leader', 'Location', 'Martian', 'Merchant', 
              'Monk', 'Mutant', 'Niffle', 'Philosopher', 'Pilot', 'Pirate', 'Politician', 'Power', 'Priest', 'Proximan', 
              'Psion', 'Quest', 'Ranger', 'Rat', 'Redacted', 'Robot', 'Scientist', 'Shapeshifter', 'Shard', 'Soldier', 
              'Specter', 'Spirit', 'Thief', 'Tree', 'Vehicle', 'Weapon', 'Witch', 'Wolf']
var ambercounts = ['0', '1', '2', '3', '4+']
var armorcounts = ['0', '1', '2', '3', '4', '5+']
var powercounts = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10+']

var joined = function (pre, ar, post, logic, filter=function(x){return x}) {
  if (ar.length > 0) {
    var nar = ar.filter(function (item) {
      return item
    })
    nar = nar.map(function (item) {
      return pre + filter(item.replace(/\_/g, '%20')) + post
    })
    if (nar.length > 0) {
      return '(' + nar.join('%20' + logic + '%20') + ')'
    }
  }
  return ''
}

var unhashImage = function(imgName) {
  var hash = md5(imgName)
  var firsthex = hash.substring(0,1)
  var first2 = hash.substring(0,2)
  return '/images/'+firsthex+'/'+first2+'/'+imgName
}

var unhashThumbImage = function(imgName) {
  var hash = md5(imgName)
  var firsthex = hash.substring(0,1)
  var first2 = hash.substring(0,2)
  return '/images/thumb/'+firsthex+'/'+first2+'/'+imgName+'/200px-'+imgName
}

var loadImage = function(image) {
  image.setAttribute('src', image.getAttribute('data-src'))
  image.onload = () => {
    image.removeAttribute('data-src')
  }
}

var padnum = function(number){
  if(number.length>=3){
    return number
  }
  var num_string = '000'+number
  return num_string.substring(num_string.length-3,num_string.length)
}

var CSearchRandom = {
  element: undefined,
  offset: 0,
  pageSize: 20,
  totalCount: 0,
  houses: [],
  types: [],
  sets: [],
  cardname: [],
  cardtext: [],
  flavortext: [],
  power_min: [""],
  power_max: [""],
  amber_min: [""],
  amber_max: [""],
  armor_min: [""],
  armor_max: [""],
  rarities: [],
  traits: [],
  cardnumber: [],
  loadingCards: false,
  loadingCount: false,
  requestcount: 0,
  numCards: 2,
  init: function (element, numCards) {
    var self=this
    this.element = element
    this.numCards = numCards
    this.newSearch()
  },
  newSearch: function() {
    var self=this
    if(self.loadingCards) self.loadingCards.abort()
    self.requestcount ++
    $(self.element).empty()
    self.load()
  },
  searchString: function () {
      console.log(this.numCards)
    this.cardnumber = []
    function getRandomInt(max) {
        return Math.floor(Math.random() * Math.floor(max)) + 1;
    }
    for(var i=0;i<this.numCards;i++){
        this.cardnumber.push("" + getRandomInt(404))
    }
    this.sets = ["Worlds Collide"]
    this.pageSize = this.numCards
    var clauses = [joined('House=%22', this.houses, '%22', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      joined('SetName=%22', this.sets, '%22', 'OR'),
      joined('Rarity=%22', this.rarities, '%22', 'OR'),
      joined('CardData.Name%20LIKE%20%22%25', this.cardname, '%25%22', 'OR'),
      joined('CardData.Traits%20LIKE%20%22%25', this.traits, '%25%22', 'OR'),
      joined('CardData.FlavorText%20LIKE%20%22%25', this.flavortext, '%25%22', 'OR'),
      joined('CardData.Text%20LIKE%20%22%25', this.cardtext, '%25%22', 'OR'),
      joined('CardNumber=%22', this.cardnumber, '%22', 'OR', padnum)
    ]
    //statQuery(clauses, {'min':this.power_min[0], 'max':this.power_max[0]}, 'Power')
    //statQuery(clauses, {'min':this.amber_min[0], 'max':this.amber_max[0]}, 'Amber')
    //statQuery(clauses, {'min':this.armor_min[0], 'max':this.armor_max[0]}, 'Armor')
    var where = joined('', clauses,
      '', 'AND')
    where = '&where=' + where
    var fieldstring = ['Name', 'House', 'Type', 'Image', 'Text'].join('%2C')
    var fields = '&fields=' + fieldstring
    // /api.php?action=cargoquery&format=json&limit=100&fields=Name%2C%20House%2C%20Type%2C%20Image%2C%20SetName&where=(House%3D%22Brobnar%22%20OR%20House%3D%22Logos%22)%20AND%20Type%3D%22Action%22%20AND%20SetName%3D%22Worlds%20Collide%22&join_on=SetData._pageName%3DCardData._pageName&offset=0
    var start = '/api.php?action=cargoquery&format=json'
    var tables = '&tables=CardData%2C%20SetData'
    var countFields = '&fields=COUNT(DISTINCT%20CardData.Name)'
    var groupby = '&group_by=' + fieldstring
    var joinon = '&join_on=SetData._pageName%3DCardData._pageName'
    var limitq = '&limit=' + this.pageSize
    var offsetq = '&offset=' + this.offset
    var q = start + tables + fields + where + joinon + groupby + limitq + offsetq
    return q
  },
  updateResults: function (resultsArray) {
    var self = this
    // Delete results tab
    var resultsTab = $(this.element)
    // For each card in query
    for (var i in resultsArray) {
      var card = resultsArray[i]
      var el = ''
      el += '<div class="header-image">'
      el += ' <a href="/' + card.title.Name + '"title="' + card.title.Name + '">'
      el += '<img class="card-' + (Number.parseInt(i)+1) + '" src="'+unhashThumbImage(card.title.Image, 200)+'" data-src="'+unhashImage(card.title.Image)+'">'
      el += '</a></div>'
      resultsTab.append(el)
    }
    /*var imgs = $('img[data-src]')
    imgs.map(function(i) {
      var self = imgs[i]
      self.onload = () => {
        loadImage(self)
      }
    })*/
  },
  load: function() {
    var self = this
    console.log(self.searchString())
    self.loadingCards = $.ajax(self.searchString(),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.updateResults(data.cargoquery)
          self.loadingCards = false
        }
      }
    )
    self.loadingCards.requestcount = self.requestcount
  },
}

function choose_random_cards() {
  console.log('initing random search')
  if ($('.random_images').length>0) {
      var element = $('.random_images')[0]
      CSearchRandom.init(element, element.getAttribute('data-number'))
  }
}

export {choose_random_cards}