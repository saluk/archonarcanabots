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
import {unhashThumbImage} from './myutils'

var wikisearch = "https://archonarcana.com/api.php?action=opensearch&format=json&formatversion=2&search={{ SEARCH }}&namespace=0&limit=10"
var resultshtml = '<div style="font-size: 15.2px; inset: 41.5167px auto auto 0.4px; width: 100%; height: auto; display: block;" class="suggestions">\
<div class="suggestions-results"></div>\
<div class="suggestions-special" style="display: block;"><div class="special-label">containing...</div><div class="special-query">{{ SEARCH }}</div></div>\
</div>'
var resulthtml = '<a href="{{ LINK }}" title="{{ NAME }}" class="mw-searchSuggest-link">\
    <div class="suggestions-result" rel="0">\
    <span class="highlight">{{ NAME_HIGHLIGHT }}</span>{{ NAME_AFTER_HIGHLIGHT }}{{ IMAGE }}</div>\
  </a>'

function miniImage(image) {
    return '   <img src="' + unhashThumbImage(image, 40) + '">'
}

class Caller {
    constructor(searchString, inputElement) {
        this.searchString = searchString
        this.inputElement = inputElement
        this.wikiResults = false
        this.cardResults = false
        this.results = []
    }
    addWikiResults(results) {
        console.log(results)
        var searchString = results[0]
        var searchNames = results[1]
        var dunno = results[2]
        var searchLinks = results[3]
        for(var i=0; i<searchNames.length; i++) {
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
        console.log(results)
        for(var i=0; i<results.length; i++) {
            var rank = 0
            if(results[i]['title']['Name'].toLowerCase().search(this.searchString) < 0) {
                rank = -1
            } else if (results[i]['title']['SearchText'].toLowerCase().search(this.searchString) < 0) {
                rank = -2
            }
            this.results.push(
                {
                    name: results[i]['title']["Name"],
                    link: '/' + results[i]['title']["Name"],
                    image: miniImage(results[i]['title']['Image']),
                    source: 'card',
                    rank: rank
                }
            )
        }
        console.log(this.results)
        this.cardResults = true
        this.finalize()
    }
    finalize() {
        if(this.wikiResults && this.cardResults) {
            this.renderResults()
        }
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

        var s = this.searchString.toLowerCase()
        for(var res of this.results) {
            var n = res.name.toLowerCase()
            var s = this.searchString.toLowerCase()
            if(n === s) {
                res.rank = 100
            }
            else if(n.search(s) >= 0){
                res.rank += 10 // Increase rank if search string is in the name
                if(n.search(s) == 0){
                    res.rank += 5 // Increase rank if search string is at the beginning of name
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
    renderResults() {
        this.filter()
        this.sort()
        console.log('render suggestions')
        $('.suggestions').remove()
        $(this.inputElement.parentElement).append(resultshtml.replace('{{ SEARCH }}', this.searchString))
        for(var result of this.results) {
            var NAME_HIGHLIGHT = ''
            var NAME_AFTER_HIGHLIGHT = result.name
            var html = resulthtml
                .replace('{{ LINK }}', result.link)
                .replace('{{ NAME }}', result.name)
                .replace('{{ NAME_HIGHLIGHT }}','')
                .replace('{{ NAME_AFTER_HIGHLIGHT }}', result.name)
                .replace('{{ IMAGE }}', result.image)
            $('.suggestions-results').append(html)
        }
        $('.suggestions').show()
    }
}

function hookTopSearch() {
    var selector = '.overridesearch #searchInput2'
    console.log('hooking top search')
    $(selector).on("input", function ontype(evt) {
        var search = this.value
        if(search.length<1) {
            $('.suggestions').empty()
            return
        }
        var caller = new Caller(search, this)
        caller.loadingWiki = $.ajax(wikisearch.replace("{{ SEARCH }}", search),
        {
            success: function (data, status, xhr) {
                caller.addWikiResults(data)
            }
        })
        var start = '/api.php?action=cargoquery&format=json'
        var tables = '&tables=CardData'
        var fields = '&fields=CardData.SearchText%2CCardData.SearchFlavorText%2CCardData.Name%2CCardData.Image'
        var limit = '&limit=10'
        var where = '&where=' + 
            'CardData.Name%20LIKE%20%22%25' + search + '%25%22' + ' OR ' +
            'CardData.SearchText%20LIKE%20%22%25' + search + '%25%22' + ' OR ' +
            'CardData.SearchFlavorText%20LIKE%20%22%25' + search + '%25%22'
        caller.loadingCards = $.ajax(
            start + tables + fields + where + limit, {
            success: function (data, status, xhr) {
                console.log(data)
                caller.addCardResults(data.cargoquery)
            },
            error: function ( jqXHR, textStatus, errorThrown ) {
                console.log(textStatus)
            }
        })
        console.log('done setting up calls')
    })
}

export {hookTopSearch}