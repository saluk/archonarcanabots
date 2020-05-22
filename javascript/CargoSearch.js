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

var check_images = {
	'Brobnar': 'https://archonarcana.com/images/e/e0/Brobnar.png',
	'Dis': 'https://archonarcana.com/images/e/e8/Dis.png',
	'Logos': 'https://archonarcana.com/images/c/ce/Logos.png',
	'Mars': 'https://archonarcana.com/images/d/de/Mars.png',
	'Sanctum': 'https://archonarcana.com/images/c/c7/Sanctum.png',
	'Saurian': 'https://archonarcana.com/images/9/9e/Saurian_P.png',
	'Star_Alliance': 'https://archonarcana.com/images/7/7d/Star_Alliance.png',
	'Shadows': 'https://archonarcana.com/images/e/ee/Shadows.png',
	'Untamed': 'https://archonarcana.com/images/b/bd/Untamed.png',
	'Anomaly': 'https://archonarcana.com/images/thumb/a/a1/Anomaly_icon.png/40px-Anomaly_icon.png'
}

class EditField {
  constructor(type, field, props) {
    this.type = type
    this.field = field
    this.label = ''
    this.split_on = ''
    this.values = []
    this.checknumbers = false
    this.divclass = ''
    this.attach = ''
    this.combo = false
    this.basic = false
    this.triggerAdvanced = false
    Object.assign(this, props)
    return this
  }
  getElement() {
    return this.getElements()[0]
  }
  getElements() {
    if(this.type === 'int') {
      return [$('[name='+this.field+'_min')[0], $('[name='+this.field+'_max')[0]]
    }
    return $('[name='+this.field+']')
  }
  addElement() {
    var self=this
    var form=self.attach
    var presetValue = parseQueryString(this.field)
    if(presetValue && !this.basic){
      this.triggerAdvanced = true
    }
    if(form === '') {
      return
    }
    if (this.type === 'br') {
      $(form).append('<br>')
    }
    if (this.type === 'text') {
      if(this.label){
        $(form).append('<label for="' + this.field + '">' + this.label + '</label>')
      }
      $(form).append('<input name="' + this.field + '" value="' + presetValue + '" />')
    }
    if (this.type === 'select') {
      var options = []
      if(this.label) {
        options.push('<label for="' + this.field + '">' + this.label + '</label>')
      }
      if(this.combo) {
        options.push('<select class="js-multiple" name="'+this.field+'" multiple>')
      } else {
        options.push('<select name="'+this.field+'">')
      }
      if(!this.combo){
        options.push('<option value=""></option>')
      }
      this.values.map(function(option) {
        var is_checked = ''
        if (presetValue.match(option)) {
          is_checked = ' selected="true"'
        }
        options.push('<option value="'+option+'"'+is_checked+'>'+option+'</option>')
      })
      options.push('</select>')
      $(form).append(options.join(''))
      if(this.combo) {
        $('[name="'+this.field+'"]').select2()
      }
    }
    if (this.type === 'checkbox') {
      //$(form).append('<span>' + this.label + ': </span>')
      this.values.map(function(value) {
        var img = check_images[value]
        var txt = ''
        txt += '<div class="'+self.divclass+'">'
        // Input
        txt += '<input type="checkbox" '
        if(img){
          txt += 'class="checkbox-house"'
        }
        if(presetValue.replace(/\+/g,' ').match(value)) {
          txt += ' checked="true" '
        }
        txt += 'name="'+self.field+'" id="'+value+'" value="'+value+'">' 
        // Label
        txt += '<label class="checkbox-label" for="'+value+'"><span class="checkbox-custom">'
        if(img){
          txt += '<span class="checkbox-checkbox"></span>'
          txt += '<img src="'+img+'" class="houseIcon">'
        } else {
          txt += value.replace(/\_/g, ' ')
        }
        txt += '</span></label></div>'
        $(form).append(txt)
      })
    }
  }
  getData() {
    if(this.type === 'text') {
      var val = this.getElement().value
      if(this.split_on.length>0) {
        return val.split(this.split_on)
      }
      return [val]
    } else if(this.type === 'select') {
      var vals = []
      if(!this.getElement().selectedOptions) {
        return vals
      }
      var opts = this.getElement().selectedOptions
      for(var i=0; i<opts.length; i++) {
        vals.push(opts[i].value)
      }
      return vals
    }
    else if(this.type === 'int') {
      return {
        min: this.getElements()[0].value,
        max: this.getElements()[1].value
      }
    }
    else if(this.type === 'checkbox') {
      var li = []
      var el = this.getElements()
      var self=this
      el.map(function(i) {
        if(el[i].checked) {
          var val = el[i].value
          if(self.checknumbers) {
            if(val==='0') {
              li.push('')
              li.push(val)
            }
          } else {
            li.push(val)
          }
        }
      })
      return li
    }
    return undefined
  }
  assignData(ob) {
    var d = this.getData()
    if(d!==undefined) {
      ob[this.field] = d
    }
  }
  listener(event) {
    if(this.type === 'text'){
      this.getElement().addEventListener('input', event)
    } else if(this.type === 'checkbox') {
      var el = this.getElements()
      el.map(function(i) {
        el[i].addEventListener('change', event)
      })
    } else if(this.type === 'int') {
      this.getElements()[0].addEventListener('input', event)
      this.getElements()[1].addEventListener('input', event)
    } else if(this.type === 'select') {
      if(this.combo){
        return $('select[name="'+this.field+'"]').select2().on('change', event)
      }
      this.getElement().addEventListener('change', event)
    }
  }
}

var minmax = function(array, field, attach, values) {
  array.push(new EditField('select', field+'_min', {'label':'Min ','attach':attach, 'values':values}))
  array.push(new EditField('select', field+'_max', {'label':'Max ','attach':attach, 'values':values}))
}

var searchFields = [
  new EditField('text', 'cardnumber', {'attach':'div.card-number-entries'}),
  new EditField('checkbox', 'houses', 
    {'label':'Houses', 'basic':true, 
     'values':houses, 'divclass':'house', 'attach':"div.house-entries"}), 
  new EditField('checkbox', 'sets', 
    {'label':'Sets', 'basic':true,
     'values':sets, 'divclass':'set', 'attach':'div.set-entries'}), 
  new EditField('checkbox', 'types', 
    {'label':'Types', 'basic':true,
     'values':types, 'divclass':'type', 'attach':'div.type-entries'}), 
  new EditField('text', 'cardname', {'attach':'div.card-name-entries', 'split_on': '|'}),
  new EditField('text', 'cardtext', {'attach':'div.card-text-entries', 'split_on': '|'}),
  new EditField('text', 'flavortext', {'attach':'div.flavor-text-entries', 'split_on': '|'}),
  new EditField('select', 'rarities', 
    {'values':rarities, 'basic':true,
     'combo': true, 'attach':'div.rarity-entries'}), 
  new EditField('select', 'traits', 
    {'values':traits, 'combo':true, 'attach':'div.trait-entries'}),
]
minmax(searchFields, 'amber', 'div.aember-entries', ambercounts)
minmax(searchFields, 'armor', 'div.armor-entries', armorcounts)
minmax(searchFields, 'power', 'div.power-entries', powercounts)


var parseQueryString = function (argument) {
  var res = '[\\?&]' + argument + '=([^&#]*)'
  var found = new RegExp(res).exec(window.location.href)
  if (found) {
    return decodeURIComponent(found[1])
  } else {
    return ''
  }
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

var statQuery = function(clauses, statInput, field) {
  if(statInput) {
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
          'CardData.'+field+' >= ' + min,
          'CardData.'+field+' <= ' + max
        ], '%20', 'AND')
      )
    }
  }
  return
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

var CSearch = {
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
    elements = elements.join('&')
    if(elements){
      elements = '?'+elements
    }
    history.replaceState({}, document.title, '/Card_Gallery'+elements)
  },
  init: function (offset, pageSize) {
    this.offset = Number.parseInt(offset)
    this.pageSize = Number.parseInt(pageSize)
    this.element = $('.card-gallery-images');
  },
  initForm: function() {
    var self=CSearch
    searchFields.map(function(field) {
      field.assignData(self)
    })
    self.offset = 0
    self.toUrl()
    self.newSearch()
  },
  newSearch: function() {
    if(CSearch.loadingCount) CSearch.loadingCount.abort()
    if(CSearch.loadingCards) CSearch.loadingCards.abort()
    CSearch.requestcount ++
    CSearch.element.empty()
    CSearch.loadCount();
    CSearch.load();
  },
  searchString: function (returnType) {
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
    statQuery(clauses, {'min':this.power_min[0], 'max':this.power_max[0]}, 'Power')
    statQuery(clauses, {'min':this.amber_min[0], 'max':this.amber_max[0]}, 'Amber')
    statQuery(clauses, {'min':this.armor_min[0], 'max':this.armor_max[0]}, 'Armor')
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
    var q
    if (returnType === 'data') {
      q = start + tables + fields + where + joinon + groupby + limitq + offsetq
    } else if (returnType === 'count') {
      q = start + tables + countFields + where + joinon
    }
    return q
  },
  updateResults: function (resultsArray) {
    var self = CSearch
    // Delete results tab
    var resultsTab = $('.card-gallery-images')
    $('.loader').remove()
    // For each card in query
    for (var i in resultsArray) {
      var card = resultsArray[i]
      var el = ''
      el += '<div class="gallery-image">'
      el += ' <a href="/' + card.title.Name + '">'
      var imgurl = '/Special:Redirect/file/' + card.title.Image
      //el += '<img width=180 src="https://archonarcana.com/index.php?title=Special:Redirect/file/' + card.title.Image + '&width=200">'
      el += '<img src="'+unhashThumbImage(card.title.Image)+'" data-src="'+unhashImage(card.title.Image)+'">'
      el += '</a></div>'
      /*if(self.texts[0]){
        el += card.title.Text
      }*/
      resultsTab.append(el)
    }
    var imgs = $('img[data-src]')
    imgs.map(function(i) {
      var self = imgs[i]
      self.onload = () => {
        loadImage(self)
      }
    })
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
    self.loadingCount = $.ajax(CSearch.searchString('count'),
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
    if(this.offset + this.pageSize >= this.totalCount){
      return false;
    }
    this.offset = this.offset + this.pageSize
    this.load()
  },
  listenScroll: function() {
    if(CSearch.loadingCards || CSearch.loadingCount){
      return false;
    }
    var height = document.documentElement.scrollHeight
    scrollOffset = document.documentElement.scrollTop + window.innerHeight;
    if (scrollOffset >= height) {
      CSearch.nextPage()
    }
  }
}

var buildCardSearchForm = function() {
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
  console.log('form built')
}

var cargoQuery = function (offset, limit) {
  // Send cargo query
  if (!offset) {
    offset = 0
  }
  buildCardSearchForm()
  CSearch.init(offset, limit)
  CSearch.initForm()
  CSearch.newSearch()
  window.addEventListener("scroll", CSearch.listenScroll);
  searchFields.map(function(field) {
    field.listener(CSearch.initForm)
  })
};

var init_cargo_search = function () {
  console.log('initing cargo search')
  if ($('.card-gallery-images').length>0) {
    cargoQuery(
      parseQueryString('DPL_offset'),
      50)
  }
}
