import {parseQueryString} from './myutils'

function perform_page_create(deck_key, div) {
    div.append('<div class="loader">Importing deck...</div>')
    $.ajax(
        'https://keyforge.tinycrease.com/generate_aa_deck_page?key='+deck_key,
        {
            success: function (data, status, xhr) {
              location.replace('https://archonarcana.com/Deck:'+deck_key+'?testjs=true')
            }
        }
    )
}

function inject_deck_data() {
    
}

function gen_deck_data() {
    var noarticle = $('.noarticletext')
    var content = $('#mw-content-text')
    var title = mw.config.values.wgTitle
    var ns = mw.config.values.wgNamespaceNumber
    if(ns != mw.config.values.wgNamespaceIds['deck']) {
        console.log('not on deck page')
        return
    }
    var deck_key = title.toLowerCase()
    if(noarticle.length > 0) {
        console.log('create new deck')
        perform_page_create(deck_key, content)
        return
    } else {
        inject_deck_data()
    }
    console.log('didnt understand deck')
}

export {gen_deck_data}