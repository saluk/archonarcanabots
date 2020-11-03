import {EditField} from './FormElements'
import {parseQueryString, unhashImage} from './myutils'
import {sets, houses, orders, getHouses} from './data'
import 'md5'
import { set_number_by_name } from './data'

var searchFields = [
  new EditField('checkbox', 'houses', 
    {'label':'Houses', 'basic':true, 
     'values':houses, 'divclass':'house', 'attach':"div.house-entries"}), 
  new EditField('text', 'deckname', {'attach':'div.deck-name-entries', 'split_on': '|', 'basic':true}),
  new EditField('checkbox', 'sets', 
    {'label':'Sets', 'basic':true,
     'values':sets, 'divclass':'set', 'attach':'div.set-entries'})
]

var getSearchField = function(field) {
  var foundField = null
  searchFields.map(function(searchField) {
    if(searchField.field===field) {
      foundField = searchField
      return
    }
  })
  return foundField
}

function htmlDecode(input){
  var e = document.createElement('div')
  e.innerHTML = input
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue
}

var DSearch = {
  element: undefined,
  houses: [],
  sets: [],
  deckname: [],
  loading: false,
  requestcount: 0,
  output_settings: {
    img_width: 200,
    img_height: 280
  },
  init: function (element) {
    var self=this
    this.element = element;
  },
  toUrl: function() {
    var elements = []
    var self = this
    searchFields.forEach(function (searchField) {
      var val = self[searchField.field]
      val = val.join('+')
      if(val) {
        elements.push(searchField.field+'='+val)
      }
    })
    if(parseQueryString('testjs')){
      elements.push('testjs='+parseQueryString('testjs'))
    }
    elements = elements.join('&')
    if(elements){
      elements = '?'+elements
    }
    var root_url = '/Template:SearchDecks'
    history.replaceState({}, document.title, root_url+elements)
  },
  initForm: function(self) {
    searchFields.map(function(field) {
      field.assignData(self)
    })
    self.offset = 0
    self.offsetActual = 0
    self.toUrl()

    // Update house selection based on sets
    var setField = getSearchField('sets')
    if(setField){
      var clicked_sets = setField.getData()
      if(clicked_sets.length>0){
        getSearchField('houses').values = getHouses(clicked_sets)
      } else {
        getSearchField('houses').values = getHouses(sets)
      }
      $(getSearchField('houses').attach).empty()
      getSearchField('houses').presetValue = self.houses.join('+')
      getSearchField('houses').addElement()
      getSearchField('houses').listener(self.initForm, self)
      getSearchField('houses').assignData(self)
    }
    self.newSearch()
  },
  newSearch: function() {
    var self=this
    self.names_used = new Set()
    self.offset = 0
    self.offsetActual = 0
    if(self.loading) self.loading.abort()
    self.requestcount ++
    self.element.empty()
    self.load();
  },
  searchString: function (returnType) {
    var where = [];
    var fields = {
      'houses': this.houses.map(function(house){
        return house.replace(/\_/,' ')
      }).join(','),
      'name': this.deckname[0],
      'expansions': this.sets.map(function(set){
        console.log(set)
        return set_number_by_name(set)
      }).join(',')
    };
    for(var field in fields) {
      if(field.length>0) {
        where.push(field+'='+fields[field])
      }
    }
    where = where.join('&')
    return 'https://keyforge.tinycrease.com/deck_query?' + where
  },
  updateResults: function (resultsArray) {
    var self = this
    // Delete results tab
    $('.loader').remove()
    $('.load_more').remove()
    // For each deck in query
    for (var i in resultsArray) {
      self.offset = self.offset + 1
      var deck = resultsArray[i]
      self.offsetActual += 1
      self.addResultDeck(deck)
    }
  },
  addResultDeck: function (deck) {
    var s = '<a href="/Deck:'+deck[0]+'?testjs=true">'+deck[1]+'</a> '
    for(var house of deck[2].split(',')) {
      house = unhashImage(house.trim().replace(' ','_')+'.png')
      s+='<img width=20 src="'+house+'">'
    }
    s+='<br>'
    this.element.append(s)
  },
  load: function() {
    this.element.append('<div class="loader">Loading...</div>')
    var self = this
    self.loading = $.ajax(this.searchString('data'),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.updateResults(data.decks)
          self.loadingCards = false
        }
      }
    )
    self.loading.requestcount = self.requestcount
  }
}

var buildDeckSearchForm = function(search) {
  searchFields.map(function(field) {
    field.addElement()
  })
  searchFields.map(function(field) {
    field.listener(search.initForm, search)
  })
  console.log('form built')
}

var init_deck_search = function () {
  console.log('initing deck search')
  if ($('.deck-gallery-images').length>0) {
    DSearch.init($('.deck-gallery-images'), 50)
    buildDeckSearchForm(DSearch)
    DSearch.initForm(DSearch)
  }
}

export {init_deck_search, DSearch}