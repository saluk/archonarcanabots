import {parseQueryString, htmlDecode, unhashThumbImage, uniques, renderWikitextToHtml} from './myutils'

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

function cards_in_text(thecards, result, rule_types) {
    return thecards.filter(function(card) {
        var name = card.card_title
        if (
            (
                (result['RulesText'].includes(name) && !result['RulesPages']) ||
                (result['RulesPages'].includes(name))
            ) && (rule_types.includes(result['RulesType']))
            && result['RulesText'].includes('//') 
        ) {
            return true;
        }
    })
}

function perform_rule_lookup(deckdata) {
    var base = '/api.php?action=cargoquery&format=json'
    var params = [
        'tables=RuleData',
        'fields=RulesText, RulesType, RulesSource, RulesPages, RulesDate',
        'group_by=RulesText, RulesType, RulesSource, RulesPages, RulesDate',
        'limit=500'
    ]
    var url = encodeURI(base+'&'+params.join('&'))
    $.ajax(
        url,
        {
            success: function (data, status, xhr) {
                $('.deck_rules').empty()
                write_rules(
                    data.cargoquery.map(function(result) {
                        return result.title
                    }),
                    deckdata.cards,
                    'FAQ'
                )
                write_rules(
                    data.cargoquery.map(function(result) {
                        return result.title
                    }),
                    deckdata.cards,
                    'FFGRuling'
                )
                write_rules(
                    data.cargoquery.map(function(result) {
                        return result.title
                    }),
                    deckdata.cards,
                    'OutstandingIssues'
                )
                write_rules(
                    data.cargoquery.map(function(result) {
                        return result.title
                    }),
                    deckdata.cards,
                    'Commentary'
                )
            }
        }
    )
}

function perform_errata_lookup(deckdata) {
    var base = '/api.php?action=cargoquery&format=json'
    var params = [
        'tables=ErrataData',
        'fields=ErrataData.Text, CONCAT(_pageTitle)=title',
        'where=Tag="latest" OR Version<>""',
        'limit=500'
    ]
    var url = encodeURI(base+'&'+params.join('&'))
    $.ajax(
        url,
        {
            success: function (data, status, xhr) {
                $('.deck_errata').empty()
                write_errata(
                    data.cargoquery.map(function(result) {
                        return result.title
                    }),
                    deckdata.cards
                )
            }
        }
    )
}

function correlate_rules_by_card(cargo_results, cards, section) {
    var texts = {}
    for(var result of cargo_results) {
        var matched = cards_in_text(cards, result, [section])
        if(matched.length==0) {
            continue
        }
        var t = result['RulesText']
        if(texts[t]) {
            texts[t]['cards'].push(...matched)
        } else {
            texts[t] = result
            texts[t]['cards'] = matched
        }
    }
    var texts_by_card_list = {}
    for(var result of Object.values(texts)) {
        result['cards'] = uniques(result['cards'], 'card_title')
        var card_list = result['cards'].map(function(card) {
            return card.card_title
        }).sort().join(',')
        console.log(card_list)
        if(texts_by_card_list[card_list]) {
            texts_by_card_list[card_list].push(result)
        } else {
            texts_by_card_list[card_list] = [result]
        }
    }
    return texts_by_card_list
}

function write_errata(cargo_results, cards) {
    var div = $('.deck_errata')
    var errata_text = ''
    for(var card of cards) {
        for(var result of cargo_results) {
            if(result.title === card.card_title) {
                errata_text += '<div class="ruling_section SectionErrata"><div class="ruling_cards">'
                errata_text += '<h2>' + gen_card_image(card, 40, 60)+card.card_title + '</h2>'
                errata_text += '</div>'
                errata_text += '<div class="ruling_text_errata">'
                errata_text += renderWikitextToHtml(result.Text)
                errata_text += '</div>'
                errata_text += '</div>'
            }
        }
    }
    if(errata_text){
        div.append('<h1>Errata</h1><br>')
        div.append(errata_text)
    }
}

function write_rules(cargo_results, cards, section) {
    console.log('write rules for'+section)
    var texts = correlate_rules_by_card(cargo_results, cards, section)
    if(Object.keys(texts).length==0) {
        return
    }
    var div = $('.deck_rules')
    div.append('<h1>'+section+'</h1><br>')
    for(var card_set of Object.keys(texts).sort()) {
        var rule_text = ''
        rule_text += '<div class="ruling_section Section'+section+'"><div class="ruling_cards">'
        rule_text += '<h2>' + texts[card_set][0]['cards'].map(
            function(card) {
                return gen_card_image(card, 40, 60)+card.card_title
            }
        ).join(', ') + '</h2>'
        rule_text += '</div>'
        for(var result of texts[card_set]) {
            var q_a = result['RulesText'].split('//')
            rule_text += '<div class="ruling_text_question">Q: '
            rule_text += renderWikitextToHtml(q_a[0])
            rule_text += '</div>'
            rule_text += '<div class="ruling_text_answer">'
            if(section=='OutstandingIssues') {
                rule_text += 'Arcana Advises: '
            } else {
                rule_text += 'A: '
            }
            rule_text += renderWikitextToHtml(q_a[1])
            rule_text += '</div>'
        }
        rule_text += '</div>'
        div.append(rule_text)
    }
}

function gen_deck_image(data, width, height) {
    return '<img src="https://images.skyjedi.com/custom/'+data.key+'/en/deck_list.png" '+
        'width='+width+' height='+height+'>'
}

function gen_card_image(card, width, height) {
    return '<img src="'+unhashThumbImage(card.image)+'" width="'+width+'" height="'+height+'"></a>'
}

function gen_cards(data) {
    var s = ''
    for(var card of data.cards) {
        s += '<a href="/'+card.card_title+'">'
        if(card.is_maverick) {
            s += 'Maverick:' + card.house
        }
        if(card.is_anomaly) {
            s += 'Anomaly:' + card.house
        }
        if(card.is_enhanced) {
            s += 'Enhanced'
        }
        s += gen_card_image(card, 140, 200)
    }
    return '<div class="card_images">'+s+'</div>'
}

function gen_rules(data) {
    perform_rule_lookup(data)
    perform_errata_lookup(data)
    return '<div class="deck_rules">Loading rules...</div>'+
        '<div class="deck_errata">Loading errata...</div>'
}

function inject_deck_data() {
    var divs = $('.deckjson')
    var out = $('.deck_contents')
	divs.map(function(id){
		var div = divs[id]
        var data = JSON.parse($(div).text())
        // TODO - change to div for production
        div = out
		$(div).empty()
        $(div).append(gen_deck_image(data, 300, 420))
        $(div).append(gen_rules(data))
        $(div).append(gen_cards(data))
		$(div)[0].style.display=""
	})
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