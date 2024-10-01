import * as $ from 'jquery'
import {unhashImage} from './myutils'

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
    this.cardnumber = []
    function getRandomInt(max) {
        return Math.floor(Math.random() * Math.floor(max)) + 1;
    }
    // TODO This randomization may not cover all of the possible cards
    for(var i=0;i<this.numCards;i++){
        this.cardnumber.push("" + getRandomInt(429))
    }
    this.pageSize = this.numCards
    var clauses = [joined('House=%22', this.houses, '%22', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      'SetInfo.IsMain=1',
      joined('Rarity=%22', this.rarities, '%22', 'OR'),
      joined('CardData.Name%20LIKE%20%22%25', this.cardname, '%25%22', 'OR'),
      joined('CardData.Traits%20LIKE%20%22%25', this.traits, '%25%22', 'OR'),
      joined('CardData.FlavorText%20LIKE%20%22%25', this.flavortext, '%25%22', 'OR'),
      joined('CardData.Text%20LIKE%20%22%25', this.cardtext, '%25%22', 'OR'),
      joined('CardNumber=%22', this.cardnumber, '%22', 'OR', padnum)
    ]
    var where = joined('', clauses,
      '', 'AND')
    where = '&where=' + where
    var fieldstring = ['Name', 'House', 'Type', 'Image', 'Text'].join('%2C')
    var fields = '&fields=' + fieldstring
    // /api.php?action=cargoquery&format=json&limit=100&fields=Name%2C%20House%2C%20Type%2C%20Image%2C%20SetName&where=(House%3D%22Brobnar%22%20OR%20House%3D%22Logos%22)%20AND%20Type%3D%22Action%22%20AND%20SetName%3D%22Worlds%20Collide%22&join_on=SetData._pageName%3DCardData._pageName&offset=0
    var start = '/api.php?action=cargoquery&format=json'
    var tables = '&tables=CardData%2C%20SetData%2C%20SetInfo'
    var countFields = '&fields=COUNT(DISTINCT%20CardData.Name)'
    var groupby = '&group_by=' + fieldstring
    var joinon = '&join_on=SetData._pageName%3DCardData._pageName%2C%20SetData.SetName%3DSetInfo.SetName'
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
      var el = '<div class="card-images-' + (Number.parseInt(i)+1) + '">\
      <img src="'+unhashImage(card.title.Image)+'" \
      alt="'+card.title.Name+'"><a href="'+card.title.Name+'">'+card.title.Name+'</a></div>'
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
  console.log('choose random')
  if ($('.random-cards').length>0) {
    var element = $('.random-cards')[0]
    CSearchRandom.init(element, element.getAttribute('data-number'))
  }
}

export {choose_random_cards}
