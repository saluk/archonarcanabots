import {EditField} from './FormElements'
import {parseQueryString, unhashImage} from './myutils'
import {sets, houses, orders, getDeckHouses} from './data'
import 'md5'
import { set_number_by_name } from './data'

`<input type="text" id="deckName" name="deckName" placeholder="Deck Name">`
var searchFields = [
  new EditField('checkbox', 'houses', 
    {'label':'Houses', 'basic':true, 
     'values':getDeckHouses(sets), 'divclass':'house', 'attach':"div.house-entries"}), 
  new EditField('text', 'deckName', {
    'split_on': '|', 'basic':true, 'attach':'div.deck-name-entries',
    'placeholder': 'Deck Name'
  }),
  new EditField('select', 'set_selected', 
    {'label':'', 'basic':true,
      'defaultlabel': 'All sets',
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
  set_selected: [],
  deckName: [],
  loading: false,
  scheduleLoading: false,
  requestcount: 0,
  pagesize: 15,
  output_settings: {
    img_width: 200,
    img_height: 280
  },
  scrollToResults: false,
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
    var setField = getSearchField('set_selected')
    if(setField){
      var clicked_sets = setField.getData()
      console.log(clicked_sets)
      if(clicked_sets.length>0){
        getSearchField('houses').values = getDeckHouses(clicked_sets)
      } else {
        getSearchField('houses').values = getDeckHouses(sets)
      }
      $(getSearchField('houses').attach).empty()
      getSearchField('houses').presetValue = self.houses.join('+')
      getSearchField('houses').addElement()
      getSearchField('houses').listener(self.initForm, self)
      getSearchField('houses').assignData(self)
    }
    self.newSearch()
  },
  newSearch: function(offset, toResults) {
    console.log(offset)
    var self=this
    self.scrollToResults = toResults
    self.names_used = new Set()
    self.offset = offset? offset : 0
    console.log(self.offset)
    if(self.loading) self.loading.abort()
    if(self.scheduleLoading) {
      window.clearInterval(self.scheduleLoading)
    }
    self.requestcount ++
    self.element[0].style.opacity = 0.5
    // No deck has 4+ houses, so lets just return nothing
    if(self.houses.length>3) {
      self.updateResults({})
      return
    }
    self.scheduleLoading = window.setTimeout(function() {
      self.load()
    }, 250)
  },
  searchString: function (returnType) {
    var where = [];
    var fields = {
      'houses': this.houses.map(function(house){
        return house.replace(/\_/,' ')
      }).join(','),
      'name': this.deckName[0],
      'expansions': this.set_selected.map(function(set){
        console.log("found-sets:"+set)
        return set_number_by_name(set)
      }).join(',')
    };
    for(var field in fields) {
      if(field.length>0) {
        where.push(field+'='+fields[field])
      }
    }
    where = where.join('&')
    where += '&page='+this.offset/this.pagesize
    return 'https://keyforge.tinycrease.com/deck_query?' + where
  },
  updateResults: function (data) {
    var self = this
    self.element.empty()
    // Delete results tab
    $('.loader').remove()
    $('.load_more').remove()
    if(!('decks' in data) || (data.decks.length==0)) {
      self.element.append('<div>No results</div>')
      return
    }
    // For each deck in query
    for (var i in data.decks) {
      var deck = data.decks[i]
      self.addResultDeck(deck)
    }
    var nav = '<div class="results-navigation">'
    if(this.offset>0) {
      nav += '<a id="dprev" href=""><img src="https://archonarcana.com/images/1/1b/Back_arrow.png" alt="Back arrow"> Previous</a>'
    }
    if(data.decks.length==this.pagesize) {
      nav += '<a id="dnext" href="">Next <img src="https://archonarcana.com/images/d/db/Noun_Arrow_5569.png" alt="Forward arrow"></a>'
    }
    nav += '</div><div></div>'
    this.element.append(nav)
    $('#dprev').on("click", function() {
      self.newSearch(self.offset-self.pagesize, true)
      return false;
    })
    $('#dnext').on("click", function() {
      self.newSearch(self.offset+self.pagesize, true)
      return false;
    })
    self.element[0].style.opacity = 1
    //if(self.scrollToResults==true) {
    //  $('.deck-results')[0].scrollIntoView(true)
    //}
  },
  addResultDeck: function (deck) {
    var s = `
    <div><a href="/Deck:${deck[0]}${parseQueryString('testjs')==='true'? '?testjs=true':''}">
    ${deck[1]}</a></div>
    <div>`
    for(var house of deck[2].split(',')) {
      house = unhashImage(house.trim().replace(' ','_')+'.png')
      s+='<img width=20 src="'+house+'">'
    }
    s+='</div>\n'
    this.element.append(s)
  },
  load: function() {
    this.element.append('<div class="loader">Loading...</div>')
    var self = this
    self.loading = $.ajax(this.searchString('data'),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.updateResults(data)
          self.loadingCards = false
        },
        error: function(req, status, error) {
          self.element.append('<div class="error">Loading failed: ' + error + '</div>')
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
  if ($('.deck-results').length>0) {
    DSearch.init($('.deck-results'))
    buildDeckSearchForm(DSearch)
    DSearch.initForm(DSearch)
  }
}

export {init_deck_search, DSearch}