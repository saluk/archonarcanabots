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
      return pre + item + post
    })
    if (nar.length > 0) {
      return '(' + nar.join('%20' + logic + '%20') + ')'
    }
  }
  return ''
}

var CSearch = {
  offset: 0,
  pageSize: 20,
  totalCount: 0,
  houses: [],
  types: [],
  sets: [],
  names: [],
  loadingCards: false,
  loadingCount: false,
  init: function (ihouses, isets, itypes, name, offset, pageSize) {
    this.houses = ihouses.split('|')
    this.types = itypes.split('|')
    this.sets = isets.split('|')
    this.names = [name]
    this.offset = Number.parseInt(offset)
    this.pageSize = Number.parseInt(pageSize)
  },
  searchString: function (returnType) {
    var where = joined('', [joined('House=%22', this.houses, '%22', 'OR'),
      joined('Type=%22', this.types, '%22', 'OR'),
      joined('SetName=%22', this.sets, '%22', 'OR'),
      joined('CardData.Name%20LIKE%20%22%25', this.names, '%25%22', 'OR')],
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
    this.loadingCards = true;
    var self = this;
    $('#cargo_results').append('<div class="loader">Loading...</div>')
    $.ajax(CSearch.searchString('data'),
      {
        success: function (data, status, xhr) {
          console.log(data)
          updateResults(data.cargoquery)
          self.loadingCards = false
        }
      }
    )
  },
  loadCount: function() {
    this.loadingCount = true;
    var self = this;
    $.ajax(CSearch.searchString('count'),
      {
        success: function (data, status, xhr) {
          self.totalCount = Number.parseInt(data.cargoquery[0].title['Name)'])
          console.log("totalcount = " + self.totalCount)
          self.loadingCount = false
          $('#result_count').append('<h2>totalCount ' + self.totalCount + '</h2>')
          // buildCargoPages(offset, totalCount, limit)
        }
      }
    )
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

var cargoQuery = function (ihouses, isets, itypes, name, offset, limit) {
  // Send cargo query
  if (!offset) {
    offset = 0
  }
  CSearch.init(ihouses, isets, itypes, name, offset, limit)
  var resultsTab = $('#cargo_results')
  resultsTab.empty()
  resultsTab.append("<span id='result_count'></span>")
  CSearch.loadCount();
  CSearch.load();
  window.addEventListener("scroll", CSearch.listenScroll);
};

var init_cargo_search = function () {
  console.log('initing cargo search')
  if (document.getElementById('cargo_results')) {
    cargoQuery(parseQueryString('DPL_arg1'),
      parseQueryString('DPL_arg2'),
      parseQueryString('DPL_arg3'),
      parseQueryString('cardname'),
      parseQueryString('DPL_offset'),
      20)
  }
}
