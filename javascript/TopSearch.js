/*
<div style="font-size: 15.2px; inset: 41.5167px auto auto 0.4px; width: 100%; height: auto; display: block;" class="suggestions">
<div class="suggestions-results">
  <a href="/index.php?search=Solo&amp;title=Special%3ASearch" title="Solo" class="mw-searchSuggest-link">
    <div class="suggestions-result" rel="0">
    <span class="highlight">So</span>lo</div>
  </a>
  <a href="/index.php?search=Soulkeeper&amp;title=Special%3ASearch" title="Soulkeeper" class="mw-searchSuggest-link">
    <div class="suggestions-result" rel="1">
    <span class="highlight">So</span>ulkeeper</div>
  </a>
  <div class="suggestions-special"></div></div>
*/
import {unhashThumbImage, unhashImage, removePunctuation, getLocale, getFullLocale, parseQueryString} from './myutils'
import $ from 'jquery';
//window.jQuery = $;
//window.$ = $;
const Bowser = require('bowser')

var wikisearch = "https://archonarcana.com/api.php?action=opensearch&format=json&formatversion=2&search={{ SEARCH }}&namespace=0&limit=10"
var advanced_search_href = `/index.php?search={{ SEARCH }}+intitle:{{ LOCALE_SEARCH }}&title=Special%3ASearch&fulltext=1&advancedSearch-current={%22fields%22%3A{%22intitle%22%3A%22{{ LOCALE_SEARCH }}%22}}`
var more = {
    'deck':`<a class="mw-searchSuggest-link" href="/Deck Search?deckName={{ SEARCH }}">
<div class="suggestions-special" style="display: block;">
<div class="special-label">Deck names containing...</div>
<div class="special-query">{{ SEARCH }}</div></div>
</a>`,
    'card':`<a class="mw-searchSuggest-link" href="/Card Gallery?cardname={{ SEARCH }}">
<div class="suggestions-special" style="display: block;">
<div class="special-label">Cards containing...</div>
<div class="special-query">{{ SEARCH }}</div></div>
</a>`,
    'wiki':`<a class="mw-searchSuggest-link" href="${advanced_search_href}">
<div class="suggestions-special" style="display: block;"><div class="special-label">containing...</div>
<div class="special-query">{{ SEARCH }}</div></div>
</a>`
}
function replace_search_href(text, search) {
    if(getLocale()=='en') {
        var locale_search = '-locale'
    } else {
        var locale_search = 'locale '+getLocale()
    }
    return text
        .replace(/\{\{ SEARCH \}\}/g, search)
        .replace(/\{\{ LOCALE_SEARCH \}\}/g, locale_search)
}
var webkit = Bowser.parse(navigator.userAgent)['browser']['name'] === 'Safari' ? 'position:relative' : ''
var resultshtml = `<div 
 style="font-size: 15.2px; inset: 41.5167px auto auto 0.4px; width: 100%; height: auto; display: block; ${webkit}" 
 class="suggestions">
<div class="suggestions-results"></div>
</div>`
var resulthtml = `<a href="{{ LINK }}" title="{{ NAME }}" class="mw-searchSuggest-link">
    <div class="suggestions-result" rel="0">
    <span class="highlight">{{ NAME_HIGHLIGHT }}</span>{{ NAME_AFTER_HIGHLIGHT }} {{ IMAGE }}
    </div>
  </a>`

var cardLimit = 100
var deckLimit = 15
var maxDecks = 5
var maxCards = 5
var maxResults = 8

function miniImage(image) {
    return '   <img src="' + unhashThumbImage(image, 40) + '">'
}

function match(search, content) {
    if(content === search){
        return "equal"
    }
    if(removePunctuation(content) === removePunctuation(search)) {
        return "equal"
    }
    var index = content.search(search)
    if(index>=0) {
        return index
    }
    index = removePunctuation(content).search(removePunctuation(search))
    return index
}

function regexEscape(s) {
    return s.replace(/\(/g, '\\(').replace(/\)/g, '\\)')
}

class Caller {
    constructor() {
        this.currentCall = 0
    }
    reset (searchString, inputElement) {
        this.currentCall += 1
        this.searchString = searchString
        this.inputElement = inputElement
        this.wikiResults = false
        this.cardResults = false
        this.deckResults = false
        this.cardsFound = 0
        this.decksFound = 0
        this.results = []
        if(this.loadingCards)
            this.loadingCards.abort()
        if(this.loadingWiki)
            this.loadingWiki.abort()        
        if(this.loadingDecks)
            this.loadingDecks.abort()
    }
    addWikiResults(results) {
        var searchString = results[0]
        var searchNames = results[1]
        var dunno = results[2]
        var searchLinks = results[3]
        for(var i=0; i<searchNames.length; i++) {
            if(searchNames[i].search(/\/locale\//) >= 0) {
                continue
            }
            this.results.push(
                {
                    name: searchNames[i],
                    link: searchLinks[i],
                    image: '',
                    source: 'wiki',
                    rank: 0
                }
            )
        }
        this.wikiResults = true
        this.finalize()
    }
    addCardResults(results) {
        for(var i=0; i<results.length; i++) {
            this.cardsFound += 1
            var rank = 0
            var searchString = regexEscape(this.searchString)
            if(results[i]['title']['Name'].toLowerCase().search(searchString) < 0) {
                rank = -1
            } else if (results[i]['title']['SearchText'] && results[i]['title']['SearchText'].toLowerCase().search(searchString) < 0) {
                rank = -2
            }
            var link = '/' + results[i]['title']["Name"]
            if(results[i]['title']['EnglishName'] && results[i]['title']['EnglishName'].length>0) {
                link = `/${results[i]['title']['EnglishName']}/locale/${getLocale()}`
            }
            this.results.push(
                {
                    name: results[i]['title']["Name"],
                    link: link,
                    image: miniImage(results[i]['title']['Image']),
                    source: 'card',
                    rank: rank
                }
            )
        }
        this.cardResults = true
        this.finalize()
    }
    addDeckResults(results) {
        for(var i=0; i<results.length; i++) {
            this.decksFound += 1
            var deck = results[i]
            var deckImg = ''
            for(var house of deck[2].split(',')) {
                house = unhashImage(house.trim().replace(' ','_')+'.png')
                deckImg+='<img width=20 src="'+house+'">'
            }
            this.results.push(
                {
                    name: deck[1],
                    link: '/Deck:' + deck[0],
                    image: deckImg,
                    source: 'deck',
                    rank: -1
                }
            )
        }
        this.deckResults = true
        this.finalize()
    }
    finalize() {
        if(this.wikiResults && this.cardResults && this.deckResults) {
            this.renderResults()
        }
    }
    rank() {
        var s = this.searchString.toLowerCase()
        for(var res of this.results) {
            var n = res.name.toLowerCase()
            var loc = match(regexEscape(s),n)
            if(loc==="equal") {
                res.rank = 100
            }
            else if(loc >= 0){
                res.rank += 10 // Increase rank if search string is in the name
                if(loc == 0){
                    res.rank += 15 // Increase rank if search string is at the beginning of name
                }
                if(res.source === 'card') {
                    res.rank += 5 // Cards rank more when they have matching text
                }
            }
        }
    }
    sort() {
        this.results.sort(function(first, second) {
            if(first.rank < second.rank) {
                return 1
            } else if (first.rank > second.rank) {
                return -1
            }
            return 0
        })
    }
    filter() {
        // If names match, use the card name
        for(var result of this.results.filter(function(res) {
            if(res.source === 'card') {
                return true
            }
            return false
        })) {
            this.results = this.results.filter(function(res) {
                if(res.source != 'card' && res.name === result.name) {
                    return false
                }
                return true
            })
        }

        var results2 = []
        var decks = 0
        var cards = 0
        var resultCount = 0
        for(var result of this.results){
            if(resultCount >= maxResults) {
                break
            }
            if(result.source === 'card') {
                if (cards >= maxCards) {
                    this.cardsFound = cardLimit  // We're hiding a result, so pretend we found a few more cards
                    continue
                }
                cards += 1
            }
            if(result.source === 'deck') {
                if (decks >= maxDecks) {
                    this.decksFound = deckLimit  // We'rd hiding a result, so pretend we found a few more decks
                    continue
                }
                decks += 1
            }
            resultCount += 1
            results2.push(result)
        }
        this.results = results2
    }
    writeResult(result) {
        var NAME_HIGHLIGHT = ''
        var NAME_AFTER_HIGHLIGHT = result.name
        var html = resulthtml
            .replace('{{ LINK }}', result.link)
            .replace('{{ NAME }}', result.name)
            .replace('{{ NAME_HIGHLIGHT }}',NAME_HIGHLIGHT)
            .replace('{{ NAME_AFTER_HIGHLIGHT }}', NAME_AFTER_HIGHLIGHT)
            .replace('{{ IMAGE }}', result.image)
        $('.suggestions-results').append(html)
    }
    renderResults() {
        this.rank()
        this.sort()
        this.filter()
        console.log('render suggestions')
        $('.suggestions').remove()
        var outhtml = resultshtml
        $(this.inputElement.parentElement).append(outhtml)
        var bestRank = {}
        for(var result of this.results) {
            if(!bestRank[result.source] || result.rank > bestRank[result.source]) {
                bestRank[result.source] = result.rank
            }
        }
        for(var group of ['card', 'wiki', 'deck']) {
            var wroteAny = false;
            for(var result of this.results.filter(r=>r.source===group)){
                this.writeResult(result)
                wroteAny = true;
            }
            if(wroteAny) {
                $('.suggestions-results').append('<hr>')
            }
        }
        for(var group of ['card', 'wiki', 'deck']) {
            if(group==='wiki' || (group==='card' && this.cardsFound >= deckLimit) || (group==='deck' && this.decksFound >= deckLimit)) {
                $('.suggestions-results').append(
                    more[group] = replace_search_href(more[group], this.searchString)
                )
            }
        }
        $('.suggestions-special').on('mouseenter', function(evt) {
            $(evt.delegateTarget).addClass('suggestions-result-current')
        })
        $('.suggestions-special').on('mouseleave', function(evt) {
            $(evt.delegateTarget).removeClass('suggestions-result-current')
        })
        $('.suggestions-result').on('mouseenter', function(evt) {
            $(evt.delegateTarget).addClass('suggestions-result-current')
        })
        $('.suggestions-result').on('mouseleave', function(evt) {
            $(evt.delegateTarget).removeClass('suggestions-result-current')
        })
        $('.suggestions').show()
        $(document).on('mouseup', function(e) 
        {
            var container = $(".suggestions")

            // if the target of the click isn't the container nor a descendant of the container
            if (!container.is(e.target) && container.has(e.target).length === 0) 
            {
                container.hide()
            }
        })
        $('#searchInput').on('click', function(evt) {
            $('.suggestions').show()
        })
    }
}

function selectLast() {
    var elements = $('.mw-searchSuggest-link')
    var last = elements[elements.length-1]
    last.focus()
}

function selectFirst() {
    var elements = $('.mw-searchSuggest-link')
    var first = elements[0]
    first.focus()
}

function hookTopSearch() {
    if(parseQueryString('oldsearch')==='true') {
        return;
    }
    //var selector = '.overridesearch #searchInput2'
    var selector = 'input#searchInput'
    console.log('hooking top search')
    var caller = new Caller()
    var placeholder = $(selector)[0].getAttribute('placeholder')
    var currentText = $(selector)[0].value
    $(selector).replaceWith(
        `<input type="search" name="search" placeholder="${placeholder}" title="Search Archon Arcana [Alt+Shift+f]" accesskey="f" id="searchInput" class="webfonts-changed" autocomplete="off">`
    )
    $('form#searchform').on('submit', function(event) {
        event.preventDefault()
        window.location.href = replace_search_href(advanced_search_href, $('input#searchInput')[0].value)
    })
    $(document).on("keypress", function (evt){
        console.log(evt)
        if($(selector).is(':focus')) {
            switch(evt.which) {
                case 38:
                    selectLast();
                    break;
                case 40:
                    selectFirst();
                    break;
            }
        }
    })
    $(selector).on("input", function ontype(evt) {
        var search = this.value
        var searchNoPunc = removePunctuation(this.value)
        caller.reset(search, this)
        if(search.length<1) {
            $('.suggestions').remove()
            return
        }
        var call = caller.currentCall
        caller.loadingWiki = $.ajax(wikisearch.replace("{{ SEARCH }}", search),
        {
            success: function (data, status, xhr) {
                if(call!=caller.currentCall)
                    return
                caller.addWikiResults(data)
            }
        })

        var start = '/api.php?action=cargoquery&format=json'
        if(getLocale() == 'en') {
            var tables = '&tables=CardData'
            var fields = '&fields=CardData.SearchText%2CCardData.SearchFlavorText%2CCardData.Name%2CCardData.Image'
            var limit = '&limit=' + cardLimit
            var where = '&where=' + 
                'CardData.Name%20LIKE%20%22%25' + searchNoPunc + '%25%22'/* + ' OR ' +
                'CardData.SearchText%20LIKE%20%22%25' + search + '%25%22' + ' OR ' +
                'CardData.SearchFlavorText%20LIKE%20%22%25' + search + '%25%22'*/
        } else {
            var tables = '&tables=CardLocaleData'
            var fields = '&fields=CardLocaleData.Name%2CCardLocaleData.Image%2CCardLocaleData.Locale%2CCardLocaleData.EnglishName'
            var limit = '&limit=' + cardLimit
            var where = `&where=CardLocaleData.Name%20LIKE%20%22%25${searchNoPunc}%25%22 AND CardLocaleData.Locale="${getFullLocale()}"`
        }
        caller.loadingCards = $.ajax(
            start + tables + fields + where + limit, {
            success: function (data, status, xhr) {
                if(call!=caller.currentCall)
                    return
                caller.addCardResults(data.cargoquery)
            },
        })

        caller.loadingDecks = $.ajax(
            'https://keyforge.tinycrease.com/deck_query?name='+search,
            {
                success: function (data, status, xhr) {
                    if(call!=caller.currentCall)
                        return
                    caller.addDeckResults(data.decks)
                },
            }
        )
        console.log('done setting up calls')
    })
    $(selector)[0].value = currentText
}

export {hookTopSearch}