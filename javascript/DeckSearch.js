var parseQueryString = function (argument) {
  var res = '[\\?&]' + argument + '=([^&#]*)'
  var found = new RegExp(res).exec(window.location.href)
  if (found) {
    return decodeURIComponent(found[1])
  } else {
    return ''
  }
}

function isElementInViewport (el) {

  // Special bonus for those using jQuery
  if (typeof jQuery === "function" && el instanceof jQuery) {
      el = el[0];
  }

  var rect = el.getBoundingClientRect();

  return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
      rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
  );
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

var unhashImage = function(imgName) {
  var hash = md5(imgName)
  var firsthex = hash.substring(0,1)
  var first2 = hash.substring(0,2)
  return '/images/'+firsthex+'/'+first2+'/'+imgName
}

var unhashThumbImage = function(imgName) {
  return 'https://archonarcana.com/thumb.php?f='+imgName+'&width=200'
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

var like_query = function(s){
  return s.replace('"', '%').replace("'", '%')
}

var DSearch = {
  element: undefined,
  offset: 0,
  pageSize: 20,
  totalCount: 0,
  deckkey: '',
  cardname: [],
  loadingDeck: false,
  loadingCards: false,
  loadingCount: false,
  requestcount: 0,
  init: function (element, pageSize) {
    var self=this
    this.offset = 0
    this.pageSize = Number.parseInt(pageSize)
    this.element = element;
    window.addEventListener("scroll", function() {
      self.listenScroll()
    })
  },
  initForm: function(self) {
    self.deckkey = parseQueryString('deck_key')
    console.log(self.deckkey)
    self.loadDeck();
    self.offset = 0
  },
  newSearch: function(self) {
    if(self.loadingCount) self.loadingCount.abort()
    if(self.loadingCards) self.loadingCards.abort()
    self.requestcount ++
    self.element.empty()
    self.loadCount();
    self.load();
  },
  searchString: function (returnType) {
    var clauses = [
      joined('RuleData.RulesText%20LIKE%20%22%25', this.cardname, '%25%22', 'OR'),
    ]
    var where = joined('', clauses,
      '', 'AND')
    where = '&where=' + where
    var fieldstring = ['RuleData.RulesText', 'RuleData.RulesType'].join('%2C')
    var fields = '&fields=' + fieldstring
    // /api.php?action=cargoquery&format=json&limit=100&fields=Name%2C%20House%2C%20Type%2C%20Image%2C%20SetName&where=(House%3D%22Brobnar%22%20OR%20House%3D%22Logos%22)%20AND%20Type%3D%22Action%22%20AND%20SetName%3D%22Worlds%20Collide%22&join_on=SetData._pageName%3DCardData._pageName&offset=0
    var start = '/api.php?action=cargoquery&format=json'
    var tables = '&tables=RuleData'
    var countFields = '&fields=COUNT(*)'
    var groupby = '&group_by=' + fieldstring
    var joinon = ''
    var limitq = '&limit=' + this.pageSize
    var offsetq = '&offset=' + this.offset
    if (returnType === 'data') {
      q = start + tables + fields + where + joinon + groupby + limitq + offsetq
    } else if (returnType === 'count') {
      q = start + tables + countFields + where + joinon + '&limit=1'
    }
    console.log(q)
    return q
  },
updateRulings: function (resultsArray) {
    var self = this
    var ffg = resultsArray
    ffg = resultsArray.filter((rule)=>{
      return rule.title.RulesType == 'FAQ' || rule.title.RulesType == 'FFGRuling'
    })
    var resultsTab = $('.deck-gallery-rulings')
    $('.loader').remove()
    $('.load_more').remove()
    // For each card in query
    for (var i in ffg) {
      var card = ffg[i]
      console.log(card)
      var el = ''
      var styl = ''
      el += '<div class="rule" style="">'
      el += card.title.RulesText
      el += '</div>'
      resultsTab.append(el)
    }
  },
  updateResults: function (resultsArray) {
    var self = this
    // Delete results tab
    var resultsTab = $('.deck-gallery-images')
    $('.loader').remove()
    $('.load_more').remove()
    // For each card in query
    for (var i in resultsArray) {
      var card = resultsArray[i]
      var el = ''
      var styl = ''
      if(card.title.Enhanced) {
        styl+= 'border-width: 6px; border-style: groove; width: 95%;'
      }
      el += '<div class="gallery-image" style="position:relative;text-align:center;">'
      el += ' <a href="/' + card.title.Name + '">'
      var imgurl = '/Special:Redirect/file/' + card.title.Image
      //el += '<img width=180 src="https://archonarcana.com/index.php?title=Special:Redirect/file/' + card.title.Image + '&width=200">'
      el += '<img style="'+styl+'" width=200 height=280 src="'+unhashThumbImage(card.title.Image)+'" data-src="'+unhashImage(card.title.Image)+'">'
      el += '<div style="position:absolute;bottom:8px;left:16px;">'+card.title.Name+'</div>'
      el += '</a>'
      el += '</div>'
      /*if(self.texts[0]){
        el += card.title.Text
      }*/
      resultsTab.append(el)
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
  loadDeck: function() {
    this.element.append('<div class="loader">Loading...</div>')
    var self = this
    self.loadingDeck = $.ajax('https://keyforge.tinycrease.com/deck?key='+self.deckkey,
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.cardname = data.cards.map((card)=>{
            return card.card_title
          })
          console.log(self.cardname)
          self.loadingDeck = false
          self.newSearch(self)
          self.updateResults(data.cards.map((card)=>{
            return {
              'title': {
                'Name':card.card_title,
                'Image':card.image_number,
                'Enhanced':card.is_enhanced
              }
            }
          }))
        }
      }
    )
    self.loadingCards.requestcount = self.requestcount
  },
  load: function() {
    this.element.append('<div class="loader">Loading...</div>')
    var self = this
    self.loadingCards = $.ajax(this.searchString('data'),
      {
        success: function (data, status, xhr) {
          if(xhr.requestcount<self.requestcount) return
          self.updateRulings(data.cargoquery)
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
    if(this.offset + this.pageSize >= this.totalCount){
      return false;
    }
    this.offset = this.offset + this.pageSize
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
    scrollOffset = document.documentElement.scrollTop + window.innerHeight;
    if (scrollOffset >= height) {
      self.nextPage()
    }
  }
}

var deckQuery = function (limit) {
  DSearch.init($('.deck-gallery-images'), limit)
  DSearch.initForm(DSearch)
};

var init_deck_search = function () {
  console.log('initing deck search')
  if ($('.deck-gallery-images').length>0) {
    deckQuery(250)
  }
}

init_deck_search()