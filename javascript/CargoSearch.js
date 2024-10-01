import {EditField} from './FormElements'
import {orders, keywords, images} from './data'
import {parseQueryString, joined, 
  getCardImage, updateCardImages, unhashImage, unhashThumbImage, renderWikitextToHtml, 
  isElementInViewport,
  pageTitle} from './myutils'
import 'md5'
import * as $ from 'jquery'

var use_locale = false

// TODO - move these to normal data when dark tidings is release
if(parseQueryString('testjs')=='true') {
  use_locale = true
}

var searchFields = [
  new EditField('checkbox', 'houses', 
    {'label':'Houses', 'basic':true, 
     'values':[], 'divclass':'house', 'attach':"div.house-entries"}), 
  new EditField('text', 'cardname', {'attach':'div.card-name-entries', 'split_on': '+', 'basic':true}),
  new EditField('checkbox', 'sets', 
    {'label':'Sets', 'basic':true,
     'values':[], 'divclass':'set', 'attach':'div.set-entries'}), 
  new EditField('checkbox', 'types', 
    {'label':'Types', 'basic':true,
     'values':[], 'divclass':'type', 'attach':'div.type-entries'}), 
  new EditField('text', 'cardtext', {'attach':'div.card-text-entries', 'split_on': '+'}),
  new EditField('text', 'flavortext', {'attach':'div.flavor-text-entries', 'split_on': '+'}),
  new EditField('text', 'cardnumber', {'attach':'div.card-number-entries'}),
  new EditField('select', 'rarities', 
    {'values':[], 'basic':true,
     'combo': true, 'attach':'div.rarity-entries'}), 
  new EditField('select', 'traits', 
    {'values':[], 'combo':true, 'attach':'div.trait-entries'}),
  new EditField('select', 'artists', 
    {'values':[], 'combo': true, 'attach': 'div.artist-entries'}),
  new EditField('select', 'cardkeywords', 
    {'values':keywords, 'combo': true, 'attach': 'div.keyword-entries'}),
  new EditField('select', 'order_by',
    {'attach':'div.order-entries', 'combo':true,
    'values':Object.keys(orders)}),
  new EditField('checkbox', 'reprints', 
      {'values':['New Cards', 'Reprints', 'Unknown'], 'basic':true,
      'attach':'div.isnew-entries'}),
  new EditField('text', 'amber_text', {'attach':'div.aember-entries', 'textsize':5}),
  new EditField('text', 'power_text', {'attach':'div.power-entries','textsize':5}),
  new EditField('text', 'armor_text', {'attach':'div.armor-entries','textsize':5}),
  new EditField('text', 'enhance_amber_text', {'attach':'div.enhance-entries',
      'textsize':5, 'label':`<img src="${images.enhanceAmber}" width="20px" class="enhance-image">`}),
  new EditField('text', 'enhance_capture_text', {'attach':'div.enhance-entries',
    'textsize':5, 'label':`<img src="${images.enhanceCapture}" width="20px" class="enhance-image">`}),
  new EditField('text', 'enhance_damage_text', {'attach':'div.enhance-entries',
    'textsize':5, 'label':`<p></p><img src="${images.enhanceDamage}" width="20px" class="enhance-image">`}),
  new EditField('text', 'enhance_draw_text', {'attach':'div.enhance-entries',
    'textsize':5, 'label':`<img src="${images.enhanceDraw}" width="20px" class="enhance-image">`}),
  new EditField('text', 'enhance_discard_text', {'attach':'div.enhance-entries',
    'textsize':5, 'label':`<img src="${images.enhanceDiscard}" width="20px" class="enhance-image">`}),
  /*new EditField('text', 'errata', 
    {'hidden':true, 'attach':'div.card-text-entries'}),
  new EditField('text', 'gigantic', 
    {'hidden':true, 'attach':'div.card-text-entries'}),*/
  /*new EditField('text', 'exclusiveSet', 
  {'hidden':true, 'attach':'div.card-text-entries'}),*/
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
  if(input) {
    e.innerHTML = input
  }
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue
}

var statQuery = function(card_db, clauses, statInput, field) {
  if(statInput) {
    var constraints = []
    if(statInput.min && statInput.min.length>0){
      var min = statInput.min.replace('+', '')
      constraints.push(`${card_db}.${field} >= ${min}`)
    }
    if(statInput.max && statInput.max.length>0){
      var max = statInput.max
      constraints.push(`${card_db}.${field} <= ${max}`)
    }
    clauses.push(joined('', constraints, '%20', 'AND'))
  }
  return
}

var padnum = function(number){
  if(number.length>=3){
    return number
  }
  var num_string = '000'+number
  return num_string.substring(num_string.length-3,num_string.length)
}

var fieldIfTrue = function(field, additional) {
  if(field && field!="") {
    return field + additional
  }
  return ''
}

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
  console.log(ret)
  return ret
}

// TODO move this to a shared set of code
// Currently we are getting metadata injected into the html and we pull that
// From the card gallery. If we want to use this metadata from the other javescript files
// We will need to inject it there too, and have a shared set of functions for dealing with it
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

var CSearch = {
  mode: 'main',
  metadata: null,
  element: undefined,
  offset: 0,
  offsetActual: 0,
  names_used: new Set(),
  pageSize: 20,
  totalCount: 0,
  houses: [],
  types: [],
  setquery: null,
  explicit_sets: null,
  sets: [],
  available_sets: [],
  cardname: [],
  cardtext: [],
  flavortext: [],
  power_text: [""],
  amber_text: [""],
  armor_text: [""],
  enhance_amber_text: [""],
  enhance_damage_text: [""],
  enhance_capture_text: [""],
  enhance_draw_text: [""],
  enhance_discard_text: [""],
  rarities: [],
  traits: [],
  artists: [],
  cardkeywords: [],
  cardnumber: [],
  order_by: [],
  errata: [false],
  gigantic: [false],
  exclusiveSet: [false],
  excludeReprints: false,
  reprints: ['New Cards', 'Reprints', 'Unknown'], //Only for spoilers
  spoilers: false,
  countField: '',
  loadingCards: false,
  loadingCount: false,
  requestcount: 0,
  output_settings: {
    img_width: 200,
    img_height: 280
  },
  init: function (element, pageSize, metadata) {
    var self=this
    self.metadata = metadata
    this.offset = 0
    this.offsetActual = 0
    this.pageSize = Number.parseInt(pageSize)
    this.element = element
    if(this.element.attr('data-mode')) {
      this.mode = this.element.attr('data-mode')
    }
    if(this.element.attr('data-setquery')) {
      this.setquery = this.element.attr('data-setquery')
    }
    if(this.element.attr('data-sets')) {
      this.explicit_sets = this.element.attr('data-sets').split(",")
    }
    this.spoilers = this.element.attr('data-spoilers')!=null;
    this.countField = this.spoilers? 'CardNumber': 'Name'
    // TODO this.mode is deprecated in favor of setquery and explicitsets
    if(this.mode !== 'main') {
      this.available_sets = [this.mode]
    } 
    if(this.explicit_sets) {
      this.available_sets = metadata.cardsets.filter(setinfo=>{
        if(this.explicit_sets.includes(setinfo["SetInfo.SetName"])){
          return true
        }
        return false
      }).map(setinfo=>{
        return setinfo["SetInfo.SetName"].replaceAll(" ","_")
      })
    }
    else if(this.setquery) {
      this.available_sets = metadata.cardsets.filter(setinfo=>{
        if(setinfo["SetInfo."+this.setquery] == "1"){
          return true
        }
        return false
      }).map(setinfo=>{
        return setinfo["SetInfo.SetName"].replaceAll(" ","_")
      })
    }
    getSearchField('types').values = getTypesFromMetadata(this.available_sets, this.metadata)
    getSearchField('rarities').values = getRaritiesFromMetadata(this.available_sets, this.metadata)
    if(this.mode==='main' && !this.spoilers) {
      this.available_sets.push("Exclude Reprints")
    }
    console.log("Available Sets:", this.available_sets)
    getSearchField('sets').values = this.available_sets

    if(this.spoilers){
      searchFields = searchFields.filter(function(field) {
        if(field.field==='sets'){
            $('.set-entries').on('click', '[name=sets]', function(e) {
              $('[name=sets]').each(function() {
                if (this != e.target)
                  $(this).prop('checked', false)
                else {
                  if($(this).prop('checked') === false) {
                    $(this).prop('checked', true)
                    return e.preventDefault()
                  }
                }
              })
            })
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

    // Change display order for KFA page
    if(self.mode !== 'main') {
      $('.house-row').remove()
      $('.set-row').remove()
      $('.rarity-row').remove()
      var a = $('.trait-row:contains(Traits)')
      //a.remove()
      var b = $('.trait-row:contains(Artists)')
      b.remove()
      var c = $('.trait-row:contains(Keywords)')
      //c.remove()
      $('.armor-row:contains(Enhance)').remove()
      //$('.third-row').empty()
      //$('.third-row').append(a)
      $('.third-row').append(b)
      //$('.third-row').append(c)
    }

    // Autoselect nearest spoiler set
    if(this.spoilers) {
      this.available_sets = [this.available_sets[0]]
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
    var root_url = pageTitle()
    history.replaceState({}, document.title, root_url+elements)
  },
  initForm: function(self) {
    if(parseQueryString('testjs')){
      if($('div.set-row')[0]){
        $('div.set-row')[0].style=''
      }
    }
    searchFields.map(function(field) {
      field.assignData(self)
    })
    self.offset = 0
    self.offsetActual = 0

    self.toUrl()

    if(self.sets.length==0 && self.spoilers) {
      $('#'+self.available_sets.slice(-1)).click()
    }

    
    // Remove reprint out of sets
    self.excludeReprints = false
    var eri = self.sets.indexOf('Exclude Reprints');
    if(eri >= 0) {
      self.sets.splice(eri, 1)
      self.excludeReprints = true
    }

    var searchingOnSets = self.sets.filter(setname => setname!='Exclude Reprints' )
    if(searchingOnSets.length==0){
      searchingOnSets = self.available_sets.filter(setname => setname!='Exclude Reprints')
    }

    console.log("searchingOnSets: "+searchingOnSets)

    // Update artists based on sets
    var available_artists = getArtistsFromMetadata(searchingOnSets, self.metadata)
    var artistField = getSearchField('artists')
    artistField.presetValue = self.artists.join('+')
    artistField.values = Array.from(available_artists).sort()
    console.log('artist preset: '+artistField.presetValue)
    console.log('artist values: '+artistField.values)
    artistField.refresh(self, self.initForm, self)

    // Update traits based which sets can be chosen
    var available_traits = getTraitsFromMetadata(searchingOnSets, self.metadata)
    var traitField = getSearchField('traits')
    traitField.presetValue = self.traits.join('+')
    traitField.values = Array.from(available_traits).sort()
    traitField.refresh(self, self.initForm, self)

    // TODO don't think we need this anymore
    if(self.mode !== 'main') {
      self.sets = [self.mode]
    }

    // Update house selection based on sets
    var setField = getSearchField('sets')
    if(setField){
      var clicked_sets = self.sets
      console.log('Get sets to build set field')
      console.log('self.sets', self.sets)
      console.log('available sets', self.available_sets)
      console.log('getHouses', getHousesFromMetadata(self.available_sets, self.metadata))
      if(clicked_sets.length>0){
        getSearchField('houses').values = getHousesFromMetadata(clicked_sets, self.metadata)
      } else {
        getSearchField('houses').values = getHousesFromMetadata(self.available_sets, self.metadata)
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
    this.cardkeywords.forEach(function(keyword) {
      keywordsToSearch.push('=%22'+keyword+'%22')
      keywordsToSearch.push('%20LIKE%20%22%25+•+'+keyword+'%22')
      keywordsToSearch.push('%20LIKE%20%22'+keyword+'+•+%25%22')
      keywordsToSearch.push('%20LIKE%20%22%25+•+'+keyword+'+•+%25%22')
    })
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
    var clauses = [joined(card_db+'.House', housesToSearch, '', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      //joined('SetName=%22', this.sets, '%22', 'OR'),
      joined('Rarity=%22', this.rarities, '%22', 'OR'),
      joined(card_db+'.Name%20LIKE%20%22%25', this.cardname, '%25%22', 'OR'),
      joined(card_db+'.Artist=%22', this.artists, '%22', 'OR'),
      joined(card_db+'.Traits', traits, '', 'OR'),
      joined(card_db+'.Keywords', keywordsToSearch, '', 'OR'),
      joined(card_db+'.SearchFlavorText%20LIKE%20%22%25', this.flavortext, '%25%22', 'OR'),
      joined(card_db+'.SearchText%20LIKE%20%22%25', this.cardtext, '%25%22', 'OR'),
      joined('CardNumber=%22', this.cardnumber, '%22', 'OR', padnum)
    ]
    var lsets = this.sets
    if (lsets.length == 0) {
      lsets = this.available_sets
    }
    if(!this.exclusiveSet[0]) {
      clauses.push(joined('SetName=%22', lsets, '%22', 'OR'))
    }
    // New exclude reprints option
    if(join_sets && this.excludeReprints) {
      clauses.push('SetData.Meta LIKE "%25Debut%25"')
    }
    statQuery(card_db, clauses, number_range(this.power_text[0]), 'Power')
    statQuery(card_db, clauses, number_range(this.amber_text[0]), 'Amber')
    statQuery(card_db, clauses, number_range(this.armor_text[0]), 'Armor')
    statQuery(card_db, clauses, number_range(this.enhance_amber_text[0]), 'EnhanceAmber')
    statQuery(card_db, clauses, number_range(this.enhance_draw_text[0]), 'EnhanceDraw')
    statQuery(card_db, clauses, number_range(this.enhance_capture_text[0]), 'EnhanceCapture')
    statQuery(card_db, clauses, number_range(this.enhance_damage_text[0]), 'EnhanceDamage')
    statQuery(card_db, clauses, number_range(this.enhance_discard_text[0]), 'EnhanceDiscard')
    if(this.errata[0]){
      clauses.push('ErrataData.Version IS NOT NULL')
    }
    if(this.spoilers && this.reprints.length>0){
      var spoilerlimit = []
      if(this.reprints.includes('New Cards')){
        spoilerlimit.push('Meta=%22SpoilerNew%22 AND Name IS NOT NULL')
      }
      if(this.reprints.includes('Reprints')){
        spoilerlimit.push('Meta=%22SpoilerReprint%22 AND Name IS NOT NULL')
      }
      if(this.reprints.includes('Unknown')){
        spoilerlimit.push('Name IS NULL OR NAME=""')
      }
      clauses.push(joined('', spoilerlimit, '', 'OR'))
    }
    var where = joined('', clauses,
      '', 'AND')
    where = '&where=' + where
    var fields_array = [card_db+'.Power', card_db+'.Rarity', card_db+'.Name', card_db+'.House', card_db+'.Type', card_db+'.Image', card_db+'.House']
    if(join_sets){
      fields_array.push('SetData.CardNumber')
    }
    fields_array.push('SetData.Meta')
    //if(!this.spoilers){
      fields_array.push(card_db+'.Text')
    //}
    if(this.spoilers){
      /*fields_array.push(card_db+'.CardNumber')*/
      fields_array.push(card_db+'.SearchText')
      fields_array.push(card_db+'.SearchFlavorText')
      fields_array.push(card_db+'.Traits')
      fields_array.push(card_db+'.Armor')
      /*fields_array.push(card_db+'.IsNew')*/
      fields_array.push(card_db+'.Source')
      fields_array.push(card_db+'.Amber')
    }
    var fieldstring = fields_array.join('%2C')
    // We need to add in row id to be able to sort by row id later, cargo api requires aliasing any keys that start with underscore in fields
    var fields = '&fields=' + fieldstring + "%2CCardData._rowID%3DRowID"
    var start = '/api.php?action=cargoquery&format=json'
    var tables = '&tables='+card_db
    if(join_sets) {
      tables += '%2C%20SetData'
    }
    var countFields = '&fields=COUNT(DISTINCT%20'+this.countField+')'
    var groupby = '&group_by=' + fieldstring + "%2CCardData._rowID"
    var joinon = ''
    if(join_sets){
      var joinon = '&join_on='+card_db+'._pageName=SetData._pageName'
    }
    // The nature of the query may duplicate a card if it is in multiple sets
    // The upper bound of the number of dupes is the number of sets we are querying on, so we should multiply how many
    // cards we request by the number of sets
    // the dupes are removed later, and the actual number of cards shown is shrunk to the page size
    var limitq = '&limit=' + this.pageSize * lsets.length
    var offsetq = '&offset=' + this.offset
    if (this.order_by.length==0){
      if(!this.spoilers && this.mode==='main'){
        this.order_by = ['House', 'Name']
      } else {
        this.order_by = ['Number']
      }
    }
    var order_by = '&order_by=' + this.order_by.map(function(order){
      return orders[order]
    }).join('%2C')
    var having = ''
    if(this.errata[0]) {
      tables += '%2C%20ErrataData'
      joinon += ','+card_db+'._pageName=ErrataData._pageName'
    }
    if(this.exclusiveSet[0]) {
      var each_set = []
      lsets.map((set)=>{
        var this_set = []
          for(const prevSet of lsets){
            if(prevSet===set){
              break
            }
            this_set.push('sum(SetData.SetName="'+prevSet.replace(/\_/g, ' ')+'")=0')
          }
        each_set.push(joined('',this_set,'','AND'))
      })
      having = '&having='+joined('',each_set,'','OR')
    }
    var q = ""
    if (returnType === 'data') {
      q = start + tables + fields + where + joinon + groupby + limitq + offsetq + having + order_by
    } else if (returnType === 'count') {
      q = start + tables + countFields + where + joinon + '&limit=1' + having
    }
    return q
  },
  outputImageResult(self,cardData) {
    if(!cardData.House) {
      cardData.House = ''
    }
    var image_number = cardData.Image
    var link = cardData.Name
    if(use_locale) {
      image_number = 'Pt-pt-'+cardData.Image
      link = cardData.Name+'/locale/pt-br'
    }
    return `
<div class="gallery-image" style="position:relative;text-align:center">
<a href="${link}">
<img id="img_+${cardData.Name.replace(/\(|\)/g,'br')}" width="${self.output_settings.img_width}" height="${self.output_settings.img_height}" src="${unhashThumbImage(cardData.Image, 200)}" data-src="${unhashImage(cardData.Image)}">
<div style="display:none;position:absolute;bottom:8px;left:16px;">${cardData.Name}</div>
</a></div>`
    return `
<div class="gallery-image" style="position:relative;text-align:center">
<a href="${link}">
${getCardImage({
  card_title: cardData.Name,
  image_number: image_number,
  house: cardData.House.split(" • ").filter(function(house){
    return (self.houses.length == 0) || (self.houses.includes(house.replace(' ', '_')))
  })[0]
}, {
  width: 200,
  outputWidth: self.output_settings.img_width,
  outputHeight: self.output_settings.img_height
})}
<div style="display:none;position:absolute;bottom:8px;left:16px;">${cardData.Name}</div>
</a></div>`
//<img id="img_'+cardData.Name.replace(/\(|\)/g,'br')+'" width='+self.output_settings.img_width+' height='+self.output_settings.img_height+' src="'+unhashThumbImage(cardData.Image, 200)+'" data-src="'+unhashImage(cardData.Image)+'">'
  },
  outputSpoilerResult(self,cardData) {
    console.log(cardData.Name)
    console.log(cardData.CardNumber)
    console.log(cardData)
    var thumbsrc = unhashThumbImage(cardData.Image, 200)
    var fullsrc = unhashImage(cardData.Image)
    var evil_twin = ""
    if(cardData.Rarity==='Evil Twin') {
      evil_twin = '<img src="https://archonarcana.com/images/4/42/Evil-twin.png" width="20px">'
    }
    var name_txt = htmlDecode(cardData.Name).replace("(Evil Twin)","")
    console.log(name_txt)
    var is_new = cardData.Meta==='SpoilerNew'
    if(is_new){
      name = '<a href="/File:IMAGE">' + name_txt + '</a>' + evil_twin
    } else {
      name = '<a href="/'+name_txt+'">' + name_txt + '</a>' + evil_twin
    }

    var el
    if(cardData.Name) {
      el = '<div class="spoilerEntry spoilerReprint">'
      if(is_new){
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
      if(!is_new) {
        el+='<div class="reprint">reprint</div>'
      }
      el += '<div class="cardInfo">'
      if((cardData.Power && cardData.Power!= "") || (cardData.Armor && cardData.Armor!="")){
        el += ' POWER power - ARMOR armor '
      }
      if(cardData.Amber && cardData.Amber!=""){
        el += ' AMBER <img src="https://archonarcana.com/images/f/fb/Enhance_aember.png" width="18px"> '
      }
      if((cardData.Power && cardData.Power!= "") || (cardData.Armor && cardData.Armor!="") || cardData.Amber){
        el += '<br>'
      }
      el += '<i>TRAITS</i><p>'
      el += 'TEXT<p><small><b>Source: </b><i>SOURCE</i></small></div>'
      el += '<div class="bottomRow"><div class="type">TYPE</div><div class="rarity">RARITY</div>'
      el += '</div></div></div>'
    } else {
      el = `
      <div class="spoilerUnknown">
      <div class="image">
        <div class="header">
          <div class="number">${htmlDecode(cardData.CardNumber)}</div>
          <div class="name"></div>
        </div>
      </div>
    </div>`
    }

    if(is_new && cardData.Name){
      el += '<div class="mobileEntry">'
      el += '<div class="newCard">new</div>'
      el += '<div class="header">\
        <div class="number">NUMBER</div><div class="name">NAME</div>\
        </div><div class="picture"><div class="floatnone">\
        <a href="/File:IMAGE" class="image">\
        <img alt="IMAGEALT" src="IMAGESRC" decoding="async" style="vertical-align: middle" width="225" height="320" data-src="IMAGEFULL"></img></a></div></div>\
        <div class="mobileText">'
      var pow = fieldIfTrue(cardData.Power, ' power')
      var arm = fieldIfTrue(cardData.Armor, ' armor')
      var amb = fieldIfTrue(cardData.Amber, ' <img src="https://archonarcana.com/images/f/fb/Enhance_aember.png" width="18px">')
      if(pow != "" && arm != "") {
        pow = pow + " - "
      }
      el += [pow, arm, amb].join(" ")
      if(pow || arm || amb) {
        el += "<br>"
      }
      el += '<i>TRAITS</i><p>TEXT<p><small><b>Source: </b><i>SOURCE</i></small></div>\
        <div class="mobileBottomRow">\
          <div class="type"><b>Type</b>: TYPE</div>\
          <div class="rarity"><b>Rarity</b>: RARITY</div>\
        </div></div>'
    } else if (cardData.Name) {
        el += `
        <div class="mobileReprint">
        <div class="reprintHeader">
          <div class="reprintNumber">${htmlDecode(cardData.CardNumber)}</div>
          <div class="reprintName"><a href="/${name_txt}" title="${name_txt}">${name_txt}</a></div>
          <div class="reprint">reprint</div>
        </div>
      </div>`
    } else {
      el += `
      <div class="mobileUnknown">
        <div class="number">${htmlDecode(cardData.CardNumber)}</div>
      </div>`
    }
  
    el = el.replace(/NAME/g,name)
    el = el.replace(/RARITY/g,htmlDecode(cardData.Rarity))
    el = el.replace(/IMAGESRC/g,thumbsrc)
    el = el.replace(/IMAGEFULL/g,fullsrc)
    el = el.replace(/IMAGE/g,htmlDecode(cardData.Image))
    el = el.replace(/NUMBER/g,htmlDecode(cardData.CardNumber))
    el = el.replace(/TEXT/g,renderWikitextToHtml(cardData.Text))
    el = el.replace(/TYPE/g,htmlDecode(cardData.Type))
    el = el.replace(/TRAITS/g,htmlDecode(cardData.Traits))
    el = el.replace(/POWER/g,htmlDecode(cardData.Power))
    el = el.replace(/ARMOR/g,htmlDecode(cardData.Armor))
    el = el.replace(/SOURCE/g,renderWikitextToHtml(cardData.Source))
    console.log(renderWikitextToHtml(cardData.Source))
    el = el.replace(/AMBER/g,htmlDecode(cardData.Amber))
    return el
  },
  updateResults: function (resultsArray) {
    var self = this
    // Delete results tab
    var resultsTab = this.element
    $('.loader').remove()
    $('.load_more').remove()
    var count_retrieved = self.pageSize
    var group_field = this.spoilers? card=>card.title.Name + card.title.CardNumber : card=>card.title.Name
    // For each card in query
    for (var i in resultsArray) {
      self.offset = self.offset + 1
      var card = resultsArray[i]
      if (self.names_used.has(group_field(card))){
        continue
      }
      self.offsetActual += 1
      if(!self.spoilers) {
        resultsTab.append(self.outputImageResult(self,card.title))
      } else {
        resultsTab.append(self.outputSpoilerResult(self,card.title))
      }
      self.names_used.add(group_field(card))
      count_retrieved -= 1
      if(count_retrieved<=0){
        break
      }
    }
    resultsTab.append('<div class="load_more"></div>')
    updateCardImages()
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
        },
        error: function(req, status, error) {
          self.element.append('<div class="error">Loading failed: ' + error + '</div>')
        }
      }
    )
    self.loadingCards.requestcount = self.requestcount
    // TODO add more features to track (and reenable mixpanel)
    /* window.mixpanel.track('gallery_search', {
      'string':this.searchString('data'), 
      'sets': this.sets,
      'houses': this.houses,
      'types': this.types,
      'cardname': this.cardname,
      'cardtext': this.cardtext,
      'flavortext': this.flavortext
    })*/
  },
  loadCount: function() {
    var self=this
    self.loadingCount = $.ajax(self.searchString('count'),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.totalCount = Number.parseInt(data.cargoquery[0].title[`COUNT(DISTINCT ${self.countField})`])
          self.loadingCount = false
          $('.cg-results').empty().append(self.totalCount + ' results')
          // buildCargoPages(offset, totalCount, limit)
        },
        error: function(req, status, error) {
          self.element.append('<div class="error">Loading failed: ' + error + '</div>')
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
    if(field.getElement()) {
      field.listener(search.initForm, search)
    }
  })
}

var init_cargo_search2 = function () {
  if ($('a[href="#tabs-4"]').length>0) {
    if (parseQueryString('traits') || parseQueryString('houses') || parseQueryString('types') || parseQueryString('rarities')) {
      $('a[href="#tabs-4"]')[0].click()
    }
  }
  var metadata = {}
  if ($('#carddata').length>0) {
    metadata = JSON.parse($('#carddata')[0].innerHTML.replace("<!--","").replace("-->",""))
  }
  if ($('.card-gallery-images').length>0) {
    CSearch.init($('.card-gallery-images'), 50, metadata)
    buildCardSearchForm(CSearch)
    CSearch.initForm(CSearch)
  }
  if ($('#cargo_results').length>0) {
    CSearch.init($('#cargo_results'), 20)
    CSearch.initElement(CSearch)
  }
}

export {init_cargo_search2, CSearch}
