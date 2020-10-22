import {EditField, minmax} from './FormElements'
import {artists, set5artists, traits, set5traits, sets, houses, spoiler_sets,
  ambercounts, armorcounts, powercounts, enhancecounts, spoilerhouses, 
  types, rarities, set5rarities, orders, keywords, features, getHouses} from './data'
import {parseQueryString, unhashImage, unhashThumbImage, isElementInViewport} from './myutils'
import 'md5'

var searchFields = [
  new EditField('checkbox', 'houses', 
    {'label':'Houses', 'basic':true, 
     'values':houses, 'divclass':'house', 'attach':"div.house-entries"}), 
  new EditField('text', 'cardname', {'attach':'div.card-name-entries', 'split_on': '|', 'basic':true}),
  new EditField('checkbox', 'sets', 
    {'label':'Sets', 'basic':true,
     'values':sets, 'divclass':'set', 'attach':'div.set-entries'}), 
  new EditField('checkbox', 'types', 
    {'label':'Types', 'basic':true,
     'values':types, 'divclass':'type', 'attach':'div.type-entries'}), 
  new EditField('text', 'cardtext', {'attach':'div.card-text-entries', 'split_on': '|'}),
  new EditField('text', 'flavortext', {'attach':'div.flavor-text-entries', 'split_on': '|'}),
  new EditField('text', 'cardnumber', {'attach':'div.card-number-entries'}),
  new EditField('select', 'rarities', 
    {'values':rarities, 'basic':true,
     'combo': true, 'attach':'div.rarity-entries'}), 
  new EditField('select', 'traits', 
    {'values':traits, 'combo':true, 'attach':'div.trait-entries'}),
  new EditField('select', 'artists', 
    {'values':artists, 'combo': true, 'attach': 'div.artist-entries'}),
  new EditField('select', 'cardkeywords', 
    {'values':keywords, 'combo': true, 'attach': 'div.keyword-entries'}),
  new EditField('select', 'order_by',
    {'attach':'div.order-entries', 'combo':true,
    'values':Object.keys(orders)}),
  new EditField('checkbox', 'reprints', 
      {'values':['New Cards', 'Reprints'], 'basic':true,
      'attach':'div.isnew-entries'}),
  /*new EditField('text', 'errata', 
    {'hidden':true, 'attach':'div.card-text-entries'}),
  new EditField('text', 'gigantic', 
    {'hidden':true, 'attach':'div.card-text-entries'}),*/
  /*new EditField('text', 'exclusiveSet', 
  {'hidden':true, 'attach':'div.card-text-entries'}),*/
]
minmax(searchFields, 'amber', 'div.aember-entries', ambercounts)
minmax(searchFields, 'armor', 'div.armor-entries', armorcounts)
minmax(searchFields, 'power', 'div.power-entries', powercounts)
minmax(searchFields, 'enhance_amber', 'div.enhance-entries', enhancecounts, true, '<img src="https://archonarcana.com/images/f/fb/Enhance_aember.png" width="20px" class="enhance-image">')
minmax(searchFields, 'enhance_capture', 'div.enhance-entries', enhancecounts, true, '<img src="https://archonarcana.com/images/f/fc/Enhance_capture.png" width="20px" class="enhance-image">')
minmax(searchFields, 'enhance_damage', 'div.enhance-entries', enhancecounts, true, '<p></p><img src="https://archonarcana.com/images/5/50/Enhance_damage.png" width="20px" class="enhance-image">')
minmax(searchFields, 'enhance_draw', 'div.enhance-entries', enhancecounts, true, '<img src="https://archonarcana.com/images/a/ac/Enhance_draw.png" width="20px" class="enhance-image">')

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

var statQuery = function(card_db, clauses, statInput, field) {
  if(statInput) {
    console.log(statInput)
    if(statInput.min===undefined || statInput.max===undefined){
      return
    }
    if(statInput.min.length>0 | statInput.max.length>0) {
      var min = statInput.min
      min = min.replace('+', '')
      if (!min) {
        min = 0
      }
      var max = statInput.max
      if (!max||max.search(/\+/)>=0) {
        max = 5000
      }
      clauses.push(
        joined('', [
          card_db+'.'+field+' >= ' + min,
          card_db+'.'+field+' <= ' + max
        ], '%20', 'AND')
      )
    }
  }
  return
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

var CSearch = {
  element: undefined,
  offset: 0,
  offsetActual: 0,
  names_used: new Set(),
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
  enhance_amber_min: [""],
  enhance_amber_max: [""],
  enhance_damage_min: [""],
  enhance_damage_max: [""],
  enhance_capture_min: [""],
  enhance_capture_max: [""],
  enhance_draw_min: [""],
  enhance_draw_max: [""],
  rarities: [],
  traits: [],
  artists: [],
  cardkeywords: [],
  cardnumber: [],
  order_by: [],
  errata: [false],
  gigantic: [false],
  exclusiveSet: [false],
  reprints: ['New Cards', 'Reprints'], //Only for spoilers
  spoilers: false,
  loadingCards: false,
  loadingCount: false,
  requestcount: 0,
  output_settings: {
    img_width: 200,
    img_height: 280
  },
  init: function (element, pageSize) {
    var self=this
    this.offset = 0
    this.offsetActual = 0
    this.pageSize = Number.parseInt(pageSize)
    this.element = element;
    this.spoilers = this.element.attr('data-spoilers')!=null;
    if(this.spoilers){
      getSearchField('houses').values = spoilerhouses
      getSearchField('rarities').values = set5rarities
      getSearchField('traits').values = set5traits
      getSearchField('artists').values = set5artists
      searchFields = searchFields.filter(function(field) {
        if(field.field==='sets'){
          return false
        }
        return true
      })
    } else {
      searchFields = searchFields.filter(function(field) {
        if(field.field==='reprints'){
          return false
        }
        return true
      })
    }
    window.addEventListener("scroll", function() {
      self.listenScroll()
    })
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
    var root_url = '/Card_Gallery'
    if(this.spoilers){
      root_url = '/Spoilers'
    }
    history.replaceState({}, document.title, root_url+elements)
  },
  initForm: function(self) {
    searchFields.map(function(field) {
      field.assignData(self)
    })
    if (self.order_by.length==0){
      if(!self.spoilers){
        self.order_by = ['House', 'Name']
      } else {
        self.order_by = ['Number']
      }
    }
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
  initElement: function(self) {
    s = this.element.attr('data-search')
    s.split(';').forEach((k)=>{
      var kv = k.split(':')
      this[kv[0]] = kv[1].split(' or ')
    })
    s = this.element.attr('data-output')
    s.split(';').forEach((k)=>{
      var kv = k.split(':')
      this.output_settings[kv[0]] = kv[1]
    })
    self.newSearch()
  },
  newSearch: function() {
    var self=this
    self.names_used = new Set()
    self.offset = 0
    self.offsetActual = 0
    if(self.loadingCount) self.loadingCount.abort()
    if(self.loadingCards) self.loadingCards.abort()
    self.requestcount ++
    self.element.empty()
    self.loadCount();
    self.load();
  },
  searchString: function (returnType) {
    var traits = []
    this.traits.forEach(function(trait) {
      traits.push('=%22'+trait+'%22')
      traits.push('%20LIKE%20%22%25+•+'+trait+'%22')
      traits.push('%20LIKE%20%22'+trait+'+•+%25%22')
      traits.push('%20LIKE%20%22%25+•+'+trait+'+•+%25%22')
    })
    var keywordsToSearch = []
    console.log(this.cardkeywords)
    this.cardkeywords.forEach(function(keyword) {
      keywordsToSearch.push('=%22'+keyword+'%22')
      keywordsToSearch.push('%20LIKE%20%22%25+•+'+keyword+'%22')
      keywordsToSearch.push('%20LIKE%20%22'+keyword+'+•+%25%22')
      keywordsToSearch.push('%20LIKE%20%22%25+•+'+keyword+'+•+%25%22')
    })
    console.log(this.cardkeywords)
    var housesToSearch = []
    this.houses.forEach(function(house) {
      housesToSearch.push('=%22'+house+'%22')
      housesToSearch.push('%20LIKE%20%22%25+•+'+house+'%22')
      housesToSearch.push('%20LIKE%20%22'+house+'+•+%25%22')
      housesToSearch.push('%20LIKE%20%22%25+•+'+house+'+•+%25%22')
    })
    if(this.gigantic[0]) {
      this.cardtext = ["other half"]
    }
    var card_db = 'CardData'
    var join_sets = true
    if(this.spoilers){
      card_db = 'SpoilerData'
      join_sets = false
    }
    var clauses = [joined(card_db+'.House', housesToSearch, '', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      //joined('SetName=%22', this.sets, '%22', 'OR'),
      joined('Rarity=%22', this.rarities, '%22', 'OR'),
      joined(card_db+'.Name%20LIKE%20%22%25', this.cardname[0].split('+'), '%25%22', 'OR'),
      joined(card_db+'.Artist=%22', this.artists, '%22', 'OR'),
      joined(card_db+'.Traits', traits, '', 'OR'),
      joined(card_db+'.Keywords', keywordsToSearch, '', 'OR'),
      joined(card_db+'.SearchFlavorText%20LIKE%20%22%25', this.flavortext[0].split('+'), '%25%22', 'OR'),
      joined(card_db+'.SearchText%20LIKE%20%22%25', this.cardtext[0].split('+'), '%25%22', 'OR'),
      joined('CardNumber=%22', this.cardnumber, '%22', 'OR', padnum)
    ]
    if(!this.exclusiveSet[0]) {
      clauses.push(joined('SetName=%22', this.sets, '%22', 'OR'))
    }
    statQuery(card_db, clauses, {'min':this.power_min[0], 'max':this.power_max[0]}, 'Power')
    statQuery(card_db, clauses, {'min':this.amber_min[0], 'max':this.amber_max[0]}, 'Amber')
    statQuery(card_db, clauses, {'min':this.armor_min[0], 'max':this.armor_max[0]}, 'Armor')
    statQuery(card_db, clauses, {'min':this.enhance_amber_min[0], 'max':this.enhance_amber_min[0]}, 'EnhanceAmber')
    statQuery(card_db, clauses, {'min':this.enhance_draw_min[0], 'max':this.enhance_draw_min[0]}, 'EnhanceDraw')
    statQuery(card_db, clauses, {'min':this.enhance_capture_min[0], 'max':this.enhance_capture_min[0]}, 'EnhanceCapture')
    statQuery(card_db, clauses, {'min':this.enhance_damage_min[0], 'max':this.enhance_damage_min[0]}, 'EnhanceDamage')
    if(this.errata[0]){
      clauses.push('ErrataData.Version IS NOT NULL')
    }
    if(this.spoilers){
      if(this.reprints.includes('New Cards')){
        clauses.push('IsNew=%22yes%22')
      }
      if(this.reprints.includes('Reprints')){
        clauses.push('IsNew IS NULL')
      }
    }
    var where = joined('', clauses,
      '', 'AND')
    where = '&where=' + where
    var fields_array = [card_db+'.Power', card_db+'.Rarity', card_db+'.Name', card_db+'.House', card_db+'.Type', card_db+'.Image']
    if(join_sets){
      fields_array.push('SetData.CardNumber')
    }
    if(!this.spoilers){
      fields_array.push(card_db+'.Text')
    }
    if(this.spoilers){
      fields_array.push(card_db+'.CardNumber')
      fields_array.push(card_db+'.SearchText')
      fields_array.push(card_db+'.SearchFlavorText')
      fields_array.push(card_db+'.Traits')
      fields_array.push(card_db+'.Armor')
      fields_array.push(card_db+'.IsNew')
      fields_array.push(card_db+'.Source')
      fields_array.push(card_db+'.Amber')
    }
    var fieldstring = fields_array.join('%2C')
    var fields = '&fields=' + fieldstring
    var start = '/api.php?action=cargoquery&format=json'
    var tables = '&tables='+card_db
    if(join_sets) {
      tables += '%2C%20SetData'
    }
    var countFields = '&fields=COUNT(DISTINCT%20'+card_db+'.Name)'
    var groupby = '&group_by=' + fieldstring
    var joinon = ''
    if(join_sets){
      var joinon = '&join_on='+card_db+'._pageName=SetData._pageName'
    }
    var limitq = '&limit=' + this.pageSize * sets.length
    var offsetq = '&offset=' + this.offset
    var order_by = '&order_by=' + this.order_by.map(function(order){
      return orders[order]
    }).join('%2C')
    var having = ''
    if(this.errata[0]) {
      tables += '%2C%20ErrataData'
      joinon += ','+card_db+'._pageName=ErrataData._pageName'
    }
    if(this.exclusiveSet[0]) {
      console.log('is exclusive')
      var each_set = []
      this.sets.map((set)=>{
        console.log('check search set'+set)
        var this_set = []
          for(const prevSet of sets){
            console.log('prevset:'+prevSet)
            if(prevSet===set){
              break
            }
            this_set.push('sum(SetData.SetName="'+prevSet.replace(/\_/g, ' ')+'")=0')
          }
        console.log(this_set)
        each_set.push(joined('',this_set,'','AND'))
      })
      console.log(each_set)
      having = '&having='+joined('',each_set,'','OR')
    }
    console.log("having="+having)
    var q = ""
    if (returnType === 'data') {
      q = start + tables + fields + where + joinon + groupby + limitq + offsetq + having + order_by
    } else if (returnType === 'count') {
      q = start + tables + countFields + where + joinon + '&limit=1' + having
    }
    console.log(q)
    return q
  },
  outputImageResult(self,cardData) {
    var el = ''
    el += '<div class="gallery-image" style="position:relative;text-align:center">'
    el += ' <a href="/' + cardData.Name + '">'
    var imgurl = '/Special:Redirect/file/' + cardData.Image
    //el += '<img width=180 src="https://archonarcana.com/index.php?title=Special:Redirect/file/' + card.title.Image + '&width=200">'
    el += '<img id="img_'+cardData.Name.replace(/\(|\)/g,'br')+'" width='+self.output_settings.img_width+' height='+self.output_settings.img_height+' src="'+unhashThumbImage(cardData.Image)+'" data-src="'+unhashImage(cardData.Image)+'">'
    el += '<div style="position:absolute;bottom:8px;left:16px;">'+cardData.Name+'</div>'
    // Card number
    // el += '<div style="position:absolute;bottom:8px;left:60px;background-color:white">'+card.title.CardNumber+'</div>'
    el += '</a>'
    el += '</div>'
    return el
  },
  outputSpoilerResult(self,cardData) {
    var thumbsrc = unhashThumbImage(cardData.Image, 200)
    var fullsrc = unhashImage(cardData.Image)

    var el = '<div class="spoilerEntry spoilerReprint">'
    if(cardData.IsNew==='yes'){
      el='<div class="spoilerEntry">'
      el+='<div class="newCard">new</div>'
    }
    el += '<div class="image"><div class="header">'
    el += '<div class="number">NUMBER</div>'
    el += '<div class="name">'
    el += 'NAME'
    el += '</div></div>'
    el += '<div class="picture"><center><div class="center"><div class="floatnone"><a href="/File:IMAGE" class="image"><img alt="IMAGEALT" src="IMAGESRC" decoding="async" style="vertical-align: middle" width="225" height="320" data-src="IMAGEFULL"></a></div></div></center></div></div>'
    el += '<div class="text"><div class="header"><div class="number">NUMBER</div><div class="name">'
    el += 'NAME'
    el += '</div></div>'
    el += '<div class="cardInfo">'
    if(cardData.Power!= "" || cardData.Armor!=""){
      el += ' POWER power - ARMOR armor '
    }
    if(cardData.Amber!=""){
      el += ' AMBER <img src="https://archonarcana.com/images/f/fb/Enhance_aember.png" width="18px"> '
    }
    if(cardData.Power!= "" || cardData.Armor!="" || cardData.Amber){
      el += '<br>'
    }
    el += '<i>TRAITS</i><p>'
    el += 'TEXT<p><small><b>Source: </b><i>SOURCE</i></small></div>'
    el += '<div class="bottomRow"><div class="type">TYPE</div><div class="rarity">RARITY</div>'
    el += '</div></div></div>'

    el += '<div class="mobileEntry">'
    if(cardData.IsNew==='yes'){
      el += '<div class="newCard">new</div>'
    }
    el += '<div class="header">\
      <div class="number">NUMBER</div><div class="name">NAME</div>\
      </div><div class="picture"><div class="floatnone">\
      <a href="/File:IMAGE" class="image">\
      <img alt="IMAGEALT" src="IMAGESRC" decoding="async" style="vertical-align: middle" width="225" height="320" data-src="IMAGEFULL"></img></a></div></div>\
      <div class="mobileText">'
    if(cardData.Power!= "" || cardData.Armor!=""){
      el += ' POWER power - ARMOR armor '
    }
    if(cardData.Amber!=""){
      el += ' AMBER <img src="https://archonarcana.com/images/f/fb/Enhance_aember.png" width="18px"> '
    }
    if(cardData.Power!= "" || cardData.Armor!="" || cardData.Amber){
      el += '<br>'
    }
    el += '<i>TRAITS</i><p>TEXT<p><small><b>Source: </b><i>SOURCE</i></small></div>\
      <div class="mobileBottomRow">\
        <div class="type"><b>Type</b>: TYPE</div>\
        <div class="rarity"><b>Rarity</b>: RARITY</div>\
      </div></div>'
    var evil_twin = ""
    if(cardData.Rarity==='Evil Twin') {
      evil_twin = '<img src="https://archonarcana.com/images/4/42/Evil-twin.png" width="20px">'
    }
    var name = htmlDecode(cardData.Name).replace("(Evil Twin)","")
    if(cardData.IsNew==='yes'){
      name = '<a href="/File:IMAGE">' + name + '</a>' + evil_twin
    } else {
      name = '<a href="/'+name+'">' + name + '</a>' + evil_twin
    }
    el = el.replace(/NAME/g,name)
    el = el.replace(/RARITY/g,htmlDecode(cardData.Rarity))
    el = el.replace(/IMAGESRC/g,thumbsrc)
    el = el.replace(/IMAGEFULL/g,fullsrc)
    el = el.replace(/IMAGE/g,htmlDecode(cardData.Image))
    el = el.replace(/NUMBER/g,htmlDecode(cardData.CardNumber))
    el = el.replace(/TEXT/g,htmlDecode(cardData.SearchText))
    el = el.replace(/TYPE/g,htmlDecode(cardData.Type))
    el = el.replace(/TRAITS/g,htmlDecode(cardData.Traits))
    el = el.replace(/POWER/g,htmlDecode(cardData.Power))
    el = el.replace(/ARMOR/g,htmlDecode(cardData.Armor))
    el = el.replace(/SOURCE/g,htmlDecode(cardData.Source))
    el = el.replace(/AMBER/g,htmlDecode(cardData.Amber))
    console.log(el)
    return el
  },
  updateResults: function (resultsArray) {
    var self = this
    // Delete results tab
    var resultsTab = this.element
    $('.loader').remove()
    $('.load_more').remove()
    var count_retrieved = self.pageSize
    // For each card in query
    for (var i in resultsArray) {
      self.offset = self.offset + 1
      var card = resultsArray[i]
      if (self.names_used.has(card.title.Name)){
        continue
      }
      self.offsetActual += 1
      if(!self.spoilers) {
        resultsTab.append(self.outputImageResult(self,card.title))
      } else {
        resultsTab.append(self.outputSpoilerResult(self,card.title))
      }
      self.names_used.add(card.title.Name)
      count_retrieved -= 1
      if(count_retrieved<=0){
        break
      }
    }
    resultsTab.append('<div class="load_more"></div>')
    var imgs = $('img[data-src]')
    imgs.map(function(i) {
      var self = imgs[i]
      self.onload = () => {
        $(self).next().remove()
        loadImage(self)
      }
    })
  },
  wikitext: function(title) {
    self.loadingWiki = $.ajax('/api.php?action=parse&format=json&text={{Spoiler Query}}&title='+title+'&contentmodel=wikitext',
      {
        success: function(data, status, xhr) {
          $('#popup').empty()
          $('#popup').append(data['parse']['text']['*'])
          self.loadingWiki = false
        }
      }
    )
  },
  load: function() {
    this.element.append('<div class="loader">Loading...</div>')
    var self = this
    self.loadingCards = $.ajax(this.searchString('data'),
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
  loadCount: function() {
    var self=this
    self.loadingCount = $.ajax(self.searchString('count'),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.totalCount = Number.parseInt(data.cargoquery[0].title['Name)'])
          self.loadingCount = false
          $('.cg-results').empty().append(self.totalCount + ' results')
          // buildCargoPages(offset, totalCount, limit)
        }
      }
    )
    self.loadingCount.requestcount = self.requestcount
  },
  nextPage: function() {
    if(this.offsetActual  >= this.totalCount){
      return false;
    }
    this.load()
  },
  listenScroll: function() {
    var self=this
    if(self.loadingCards || self.loadingCount){
      return false
    }
    if(isElementInViewport($('.load_more'))){
      self.nextPage()
      return true
    }
    var height = document.documentElement.scrollHeight
    var scrollOffset = document.documentElement.scrollTop + window.innerHeight;
    if (scrollOffset >= height) {
      self.nextPage()
    }
  }
}

var buildCardSearchForm = function(search) {
  //$('#viewcards_form').append('<form method="GET" id="searchForm"></form>')
  var triggerAdvanced = false;
  searchFields.map(function(field) {
    field.addElement()
    if(field.triggerAdvanced){
      triggerAdvanced = true
    }
  })
  $('.advanced-search')[0].addEventListener("click", function(evt) {
    var on = $('.cg-advanced-menu')[0].style.display !== 'none'
    if(on) {
      $('.cg-advanced-menu')[0].style = 'display:none;'
      $('.advanced-search-icon')[0].style = ''
    } else {
      $('.cg-advanced-menu')[0].style = ''
      $('.advanced-search-icon')[0].style = 'transform:rotate(180deg)'
    }
  })
  if(triggerAdvanced) {
    $('.advanced-search')[0].click()
  }
  searchFields.map(function(field) {
    field.listener(search.initForm, search)
  })
  console.log('form built')
}

var init_cargo_search2 = function () {
  console.log('initing cargo search updated')
  if ($('.card-gallery-images').length>0) {
    CSearch.init($('.card-gallery-images'), 50)
    buildCardSearchForm(CSearch)
    CSearch.initForm(CSearch)
  } else if($('.spoilerOuter').length>0) {
    CSearch.init($('.spoilerOuter'), 50)
    buildCardSearchForm(CSearch)
    CSearch.initForm(CSearch)
  }
  if ($('#cargo_results').length>0) {
    CSearch.init($('#cargo_results'), 20)
    CSearch.initElement(CSearch)
  }
}

export {init_cargo_search2, CSearch}