import {parseQueryString} from './myutils'

function perform_page_create(deck_key, recreate, div) {
    div.append('<div class="loader">Importing deck...</div>')
    $.ajax(
        'https://keyforge.tinycrease.com/generate_aa_deck_page?key='+deck_key+'&recreate='+recreate,
        {
            success: function (data, status, xhr) {
              location.replace('https://archonarcana.com/Deck:'+deck_key+'?testjs=true')
            }
        }
    )
}

function gen_deck_data() {
    var recreate = parseQueryString('recreate');
    var noarticle = $('.noarticletext')
    var content = $('#mw-content-text')
    var title = mw.config.values.wgTitle
    var ns = mw.config.values.wgNamespaceNumber
    if(ns != mw.config.values.wgNamespaceIds['deck']) {
        console.log('not on deck page')
        return
    }
    var deck_key = title
    console.log(deck_key)
    console.log(noarticle.length)
    console.log(content.length)
    console.log(recreate)
    if(noarticle.length > 0) {
        console.log('create new deck')
        perform_page_create(deck_key, recreate, noarticle)
        return
    }
    if(content.length > 0 && recreate==='1') {
        console.log('recreate deck')
        content.replaceWith('')
        perform_page_create(deck_key, recreate, content)
        return
    }
    console.log('didnt understand deck')
}

export {gen_deck_data}