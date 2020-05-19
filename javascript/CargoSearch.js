var houses = ['Brobnar','Dis','Logos','Mars','Sanctum','Saurian','Star_Alliance','Shadows','Untamed','Anomaly']
var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation']
var types = ['Creature', 'Artifact', 'Upgrade', 'Action']
var rarities = ['Common', 'Uncommon', 'Rare', 'Fixed']
var traits = ['AI', 'Agent', 'Alien', 'Ally', 'Angel', 'Aquan', 'Beast', 'Cyborg', 'Demon', 'Dinosaur', 'Dragon', 'Elf', 
              'Equation', 'Experiment', 'Faerie', 'Fungus', 'Giant', 'Goblin', 'Handuhan', 'Horseman', 'Human', 'Hunter', 
              'Imp', 'Insect', 'Item', 'Jelly', 'Knight', 'Krxix', 'Law', 'Leader', 'Location', 'Martian', 'Merchant', 
              'Monk', 'Mutant', 'Niffle', 'Philosopher', 'Pilot', 'Pirate', 'Politician', 'Power', 'Priest', 'Proximan', 
              'Psion', 'Quest', 'Ranger', 'Rat', 'Redacted', 'Robot', 'Scientist', 'Shapeshifter', 'Shard', 'Soldier', 
              'Specter', 'Spirit', 'Thief', 'Tree', 'Vehicle', 'Weapon', 'Witch', 'Wolf']
var ambercounts = ['0', '1', '2', '3', '4']
var armorcounts = ['0', '1', '2', '3', '4', '5']

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
  constructor(type, field, label, split_on='', values=[], checknumbers=false) {
    this.type = type
    this.field = field
    this.label = label
    this.split_on = split_on
    this.values = values
    this.checknumbers = checknumbers
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
  addElement(form) {
    var self=this
    if (this.type === 'br') {
      $(form).append('<br>')
    }
    if (this.type === 'text') {
      $(form).append('<label for="' + this.field + '">' + this.label + ': </label>')
      $(form).append('<input name="' + this.field + '" value="' + parseQueryString(this.field) + '" />')
    }
    if (this.type === 'int') {
      $(form).append([
        '<label for="' + this.field + '">' + this.label + ': </label>',
        '<input type="number" name="' + this.field + '_min" min="0" max="50" width="5">',
        '<input type="number" name="' + this.field + '_max" min="0" max="50" width="5">'
      ].join(''))
    }
    if (this.type === 'select') {
      var options = ['<select name="'+this.field+'">']
      options.push('<option value="">All '+this.label+'</option>')
      this.values.map(function(option) {
        options.push('<option value="'+option+'">'+option+'</option>')
      })
      options.push('</select>')
      $(form).append(options.join(''))
    }
    if (this.type === 'checkbox') {
      $(form).append('<span>' + this.label + ': </span>')
      this.values.map(function(value) {
        var img = check_images[value]
        var txt = ''
        // Input
        txt += '<input type="checkbox" '
        if(img){
          txt += 'class="checkbox-house"'
        }
        if(parseQueryString(self.field).replace(/\+/g,' ').match(value)) {
          txt += ' checked="true" '
        }
        txt += 'name="'+self.field+'" id="'+value+'" value="'+value+'">' 
        // Label
        txt += '<label class="checkbox-label" for="'+value+'"><span class="checkbox-custom">'
        if(img){
          txt += '<span class="checkbox-checkbox"></span>'
          txt += '<img src="'+img+'">'
        } else {
          txt += value.replace(/\_/g, ' ')
        }
        txt += '</span></label>'
        $(form).append(txt)
      })
    }
  }
  getData() {
    console.log('getData')
    console.log(this)
    if(this.type === 'text' || this.type === 'select') {
      var val = this.getElement().value
      if(this.split_on.length>0) {
        return val.split(this.split_on)
      }
      return [val]
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
      this.getElement().addEventListener('change', event)
    }
  }
}

var searchFields = [
  new EditField('text', 'cardnumber', 'Card Number'), new EditField('br'),
  new EditField('checkbox', 'houses', 'Houses', '', houses), new EditField('br'),
  new EditField('checkbox', 'sets', 'Sets', '', sets), new EditField('br'),
  new EditField('checkbox', 'types', 'Types', '', types), new EditField('br'),
  new EditField('text', 'cardname', 'Card Name'),
  new EditField('text', 'cardtext', 'Card Text', '|'),
  new EditField('text', 'flavortext', 'Flavor Text', '|'), new EditField('br'),
  new EditField('int', 'power', 'Power (min/max)'), new EditField('br'),
  new EditField('int', 'amber', 'Aember', '', ambercounts), new EditField('br'),
  new EditField('int', 'armor', 'Armor', '', armorcounts), new EditField('br'),
  new EditField('select', 'rarities', 'Rarities', '', rarities), new EditField('br'),
  new EditField('select', 'traits', 'Traits', '', traits), new EditField('br'),
]


var parseQueryString = function (argument) {
  console.log(window.location.href)
  var res = '[\\?&]' + argument + '=([^&#]*)'
  console.log(res)
  var found = new RegExp(res).exec(window.location.href)
  if (found) {
    return decodeURIComponent(found[1])
  } else {
    return ''
  }
}

var joined = function (pre, ar, post, logic, evaltype='string') {
  if (ar.length > 0) {
    var nar = ar.filter(function (item) {
      return item
    })
    nar = nar.map(function (item) {
      if(evaltype == 'number') {
        if(item.search(/\+/)<0){
          return pre + '=%22' + item + post
        } else {
          item = item.substring(0, item.search(/\+/))
          return pre + '>%22' + item + post
        }
      }
      return pre + item.replace(/\_/g, '%20') + post
    })
    if (nar.length > 0) {
      return '(' + nar.join('%20' + logic + '%20') + ')'
    }
  }
  return ''
}

var statQuery = function(statInput, field) {
  if(statInput) {
    if(statInput.min | statInput.max) {
      var min = statInput.min
      if (!min) {
        min = 0
      }
      var max = statInput.max
      if (!max) {
        max = 5000
      }
      return joined('', [
          'CardData.'+field+' >= ' + min,
          'CardData.'+field+' <= ' + max
        ], '%20', 'AND')
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
  power: [],
  amber: [],
  armor: [],
  rarities: [],
  traits: [],
  cardnumber: [],
  loadingCards: false,
  loadingCount: false,
  requestcount: 0,
  init: function (offset, pageSize) {
    this.offset = Number.parseInt(offset)
    this.pageSize = Number.parseInt(pageSize)
    this.element = $('#cargo_results');
  },
  initForm: function() {
    var self=CSearch
    searchFields.map(function(field) {
      field.assignData(self)
    })
    self.offset = 0
    self.newSearch()
  },
  newSearch: function() {
    if(CSearch.loadingCount) CSearch.loadingCount.abort()
    if(CSearch.loadingCards) CSearch.loadingCards.abort()
    CSearch.requestcount ++
    CSearch.element.empty()
    CSearch.element.append("<span id='result_count'></span>")
    CSearch.loadCount();
    CSearch.load();
  },
  searchString: function (returnType) {
    var clauses = [joined('House=%22', this.houses, '%22', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      joined('SetName=%22', this.sets, '%22', 'OR'),
      joined('Rarity=%22', this.rarities, '%22', 'OR'),
      joined('Amber=%22', this.amber, '%22', 'OR'),
      joined('Armor', this.armor, '%22', 'OR', 'number'),
      joined('CardData.Name%20LIKE%20%22%25', this.cardname, '%25%22', 'OR'),
      joined('CardData.Traits%20LIKE%20%22%25', this.traits, '%25%22', 'OR'),
      joined('CardData.FlavorText%20LIKE%20%22%25', this.flavortext, '%25%22', 'OR'),
      joined('CardData.Text%20LIKE%20%22%25', this.cardtext, '%25%22', 'OR'),
      joined('CardNumber=%22', this.cardnumber, '%22', 'OR')
    ]
    var stat = statQuery(this.power, 'Power')
    if(stat){
      clauses.push(stat)
    }
    var stat = statQuery(this.amber, 'Amber')
    if(stat){
      clauses.push(stat)
    }
    var stat = statQuery(this.armor, 'Armor')
    if(stat){
      clauses.push(stat)
    }
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
    console.log('pagesize' + this.pageSize)
    var limitq = '&limit=' + this.pageSize
    var offsetq = '&offset=' + this.offset
    var q
    console.log('search string checking')
    if (returnType === 'data') {
      q = start + tables + fields + where + joinon + groupby + limitq + offsetq
    } else if (returnType === 'count') {
      q = start + tables + countFields + where + joinon
    }
    console.log('ajax:' + q)
    return q
  },
  updateResults: function (resultsArray) {
    var self = CSearch
    console.log(resultsArray)
    // Delete results tab
    var resultsTab = $('#cargo_results')
    $('.loader').remove()
    // For each card in query
    for (var i in resultsArray) {
      var card = resultsArray[i]
      var el = ''
      el += ' <a href="/' + card.title.Name + '">'
      var imgurl = '/Special:Redirect/file/' + card.title.Image
      //el += '<img width=180 src="https://archonarcana.com/index.php?title=Special:Redirect/file/' + card.title.Image + '&width=200">'
      el += '<img width=180 height=252 src="'+unhashThumbImage(card.title.Image)+'" data-src="'+unhashImage(card.title.Image)+'">'
      el += '</a> '
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
          console.log(data)
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
          console.log("totalcount = " + self.totalCount)
          self.loadingCount = false
          $('#result_count').append('<h2>totalCount ' + self.totalCount + '</h2>')
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
  $('#viewcards_form').append('<form method="GET" id="searchForm"></form>')
  searchFields.map(function(field) {
    field.addElement('#searchForm')
  })
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
  if (document.getElementById('cargo_results')) {
    cargoQuery(
      parseQueryString('DPL_offset'),
      50)
  }
}
