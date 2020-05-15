var houses = ['Brobnar','Dis','Logos','Mars','Sanctum','Saurian','Star_Alliance','Shadows','Untamed','Anomaly']
var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation']
var types = ['Creature', 'Artifact', 'Upgrade', 'Action']
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
  constructor(type, field, label, split_on='', values=[]) {
    this.type = type
    this.field = field
    this.label = label
    this.split_on = split_on
    this.values = values
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
          xt += ' checked="true" '
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
    if(this.type === 'text') {
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
      el.map(function(i) {
        if(el[i].checked) {
          li.push(el[i].value)
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
    }
  }
}

var searchFields = [
  new EditField('checkbox', 'houses', 'Houses', '', houses), new EditField('br'),
  new EditField('checkbox', 'sets', 'Sets', '', sets), new EditField('br'),
  new EditField('checkbox', 'types', 'Types', '', types), new EditField('br'),
  new EditField('text', 'cardname', 'Card Name'),
  new EditField('text', 'cardtext', 'Card Text', '|'),
  new EditField('text', 'flavortext', 'Flavor Text', '|'), new EditField('br'),
  new EditField('int', 'power', 'Power (min/max)'), new EditField('br'),
  new EditField('int', 'amber', 'Aember (min/max)'), new EditField('br'),
  new EditField('int', 'armor', 'Armor (min/max)'), new EditField('br')
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

var joined = function (pre, ar, post, logic) {
  if (ar.length > 0) {
    var nar = ar.filter(function (item) {
      return item
    })
    nar = nar.map(function (item) {
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
    joined('CardData.Name%20LIKE%20%22%25', this.cardname, '%25%22', 'OR'),
    joined('CardData.FlavorText%20LIKE%20%22%25', this.flavortext, '%25%22', 'OR'),
    joined('CardData.Text%20LIKE%20%22%25', this.cardtext, '%25%22', 'OR')
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
      //el += '<img src="'+imgurl+'" decoding="async" srcset="'+imgurl+'&width=200 1.5x, '+imgurl+' 2x" data-file-width="600" data-file-height="840" width="200">'
      el += '<img width=180 src="https://archonarcana.com/index.php?title=Special:Redirect/file/' + card.title.Image + '&width=200">'
      el += '</a> '
      /*if(self.texts[0]){
        el += card.title.Text
      }*/
      resultsTab.append(el)
    }
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
