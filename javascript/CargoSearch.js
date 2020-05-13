var houses = ['Brobnar','Dis','Logos','Mars','Sanctum','Saurian','Star_Alliance','Shadows','Untamed','Anomaly'];
var sets = ['Call_of_the_Archons', 'Age_of_Ascension', 'Worlds_Collide', 'Mass_Mutation'];
var types = ['Creature', 'Artifact', 'Upgrade', 'Action'];

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

var updateResults = function (resultsArray) {
  console.log(resultsArray)
  // Delete results tab
  var resultsTab = $('#cargo_results')
  $('.loader').remove()
  // For each card in query
  for (var i in resultsArray) {
    var card = resultsArray[i]
    var el = ''
    el += ' <a href="/' + card.title.Name + '">'
    // el += '<img alt="452-101.png" src="/images/thumb/1/17/452-101.png/300px-452-101.png" decoding="async" srcset="/images/thumb/1/17/452-101.png/450px-452-101.png 1.5x, /images/1/17/452-101.png 2x" data-file-width="600" data-file-height="840" width="300" height="420">'
    el += '<img width=200 src="https://archonarcana.com/index.php?title=Special:Redirect/file/' + card.title.Image + '&width=200">'
    el += '</a> '
    resultsTab.append(el)
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

var CSearch = {
  element: undefined,
  offset: 0,
  pageSize: 20,
  totalCount: 0,
  houses: [],
  types: [],
  sets: [],
  names: [],
  texts: [],
  loadingCards: false,
  loadingCount: false,
  requestcount: 0,
  init: function (ihouses, isets, itypes, name, itexts, offset, pageSize) {
    this.houses = ihouses.split('|')
    this.types = itypes.split('|')
    this.sets = isets.split('|')
    this.names = [name]
    this.texts = itexts.split('|')
    console.log(this.texts)
    this.offset = Number.parseInt(offset)
    this.pageSize = Number.parseInt(pageSize)
    this.element = $('#cargo_results');
    if(this.element.attr('data-houses')) {
      this.houses = this.element.attr('data-houses').split('|')
    }
  },
  initForm: function() {
    var self=CSearch
    var ihouses = []
    houses.map(function(house) {
      var box = $('#category_' + house)
      if(box[0].checked) {
        ihouses.push(house)
      }
    })
    self.houses = ihouses;
    var isets = []
    sets.map(function(set) {
      var box = $('#category_' + set)
      if(box[0].checked) {
        isets.push(set)
      }
    })
    self.sets = isets;
    var itypes = []
    types.map(function(t) {
      var box = $('#category_' + t)
      if(box[0].checked) {
        itypes.push(t)
      }
    })
    self.types = itypes;
    self.names = [$('[name=cardname]')[0].value]
    self.texts = $('[name=cardtext]')[0].value.split('|')
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
    var where = joined('', [joined('House=%22', this.houses, '%22', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      joined('SetName=%22', this.sets, '%22', 'OR'),
      joined('CardData.Name%20LIKE%20%22%25', this.names, '%25%22', 'OR'),
      joined('', [
        joined('CardData.Text%20LIKE%20%22%25', this.texts, '%25%22', 'OR'),
        joined('CardData.FlavorText%20LIKE%20%22%25', this.texts, '%25%22', 'OR')],
        '', 'OR')
      ],
      '', 'AND')
    where = '&where=' + where
    var fields = ['Name', 'House', 'Type', 'Image'].join('%2C')
    fields = '&fields=' + fields
    // /api.php?action=cargoquery&format=json&limit=100&fields=Name%2C%20House%2C%20Type%2C%20Image%2C%20SetName&where=(House%3D%22Brobnar%22%20OR%20House%3D%22Logos%22)%20AND%20Type%3D%22Action%22%20AND%20SetName%3D%22Worlds%20Collide%22&join_on=SetData._pageName%3DCardData._pageName&offset=0
    var start = '/api.php?action=cargoquery&format=json'
    var tables = '&tables=CardData%2C%20SetData'
    var countFields = '&fields=COUNT(DISTINCT%20CardData.Name)'
    var groupby = '&group_by=Name%2C%20House%2C%20Type%2C%20Image'
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
  load: function() {
    this.element.append('<div class="loader">Loading...</div>')
    var self = this
    self.loadingCards = $.ajax(this.searchString('data'),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          console.log(data)
          updateResults(data.cargoquery)
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

var cargoQuery = function (ihouses, isets, itypes, name, itexts, offset, limit) {
  // Send cargo query
  if (!offset) {
    offset = 0
  }
  CSearch.init(ihouses, isets, itypes, name, itexts, offset, limit)
  CSearch.newSearch();
  window.addEventListener("scroll", CSearch.listenScroll);
  $('[type=checkbox][name=category]').map(function (i) {
    $('[type=checkbox][name=category]')[i].addEventListener('change', CSearch.initForm)
  })
  $('[name=cardtext]').map(function (i) {
    $('[name=cardtext]')[i].addEventListener('input', CSearch.initForm)
  })
  $('[name=cardname]').map(function (i) {
    $('[name=cardname]')[i].addEventListener('input', CSearch.initForm)
  })
};

var init_cargo_search = function () {
  console.log('initing cargo search')
  init_dpl_search(10);
  if (document.getElementById('cargo_results')) {
    cargoQuery(parseQueryString('DPL_arg1'),
      parseQueryString('DPL_arg2'),
      parseQueryString('DPL_arg3'),
      parseQueryString('cardname'),
      parseQueryString('cardtext'),
      parseQueryString('DPL_offset'),
      20)
  }
}
