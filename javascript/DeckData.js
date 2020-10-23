import {parseQueryString, htmlDecode, unhashThumbImage, uniques, renderWikitextToHtml, collapsible_block} from './myutils'
import {cardCombos, images, set_name_by_number} from './data'

function perform_page_create(deck_key, div) {
    div.append('<div class="loader">Importing deck...</div>')
    $.ajax(
        'https://keyforge.tinycrease.com/generate_aa_deck_page?key='+deck_key,
        {
            success: function (data, status, xhr) {
                setTimeout(
                    function() {
                        location.replace('https://archonarcana.com/Deck:'+deck_key+'?testjs=true')
                    },
                    2000
                )
            }
        }
    )
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
                    uniques(deckdata.cards, 'card_title')
                )
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
        ) {
            return true;
        }
    })
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
                errata_text += '<i>Should Read:</i> ' + renderWikitextToHtml(result.Text)
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
    var s = ''
    //div.append('<h1>'+section+'</h1><br>')
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
            if(q_a.length==2) {
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
            } else {
                rule_text += '<div class="ruling_text_commentary">'+
                    renderWikitextToHtml(q_a[0])+'</div>'
            }
        }
        rule_text += '</div>'
        s += rule_text
    }
    div.append(collapsible_block(0, section, s))
}

function gen_deck_image(data, width, height) {
    var lang = Object.keys(mw.language.data)[0]
    if(!['en','es','it','de','fr','pl','pt','th','zh'].includes(lang)) {
        lang = 'en'
    }
    return '<img src="https://images.skyjedi.com/custom/'+data.key+'/'+lang+'/deck_list.png" '+
        'width='+width+' height='+height+'>'
}

function gen_card_image(card, width, height, css) {
    if(!css) {
        css = ''
    }
    var image = unhashThumbImage(card.image_number, 200)
    if(card.subtype && card.subtype.match(/gigantic/i)) {
        image = card.front_image
    }
    var s = '<a href="/'+card.card_title+'">'
    s += '<img class="'+css+'" src="'+image+'" width="'+width+'" height="'+height+'"></a>'
    return s
}

function gen_cards(data) {
    var s = ''
    var houses = [];
    for(var card of data.cards) {
        var classes = ['card_image']
        if(card.is_maverick) {
            classes.push(card.house)
            classes.push('maverick')
        }
        if(card.is_anomaly) {
            classes.push(card.house)
            classes.push('anomaly')
        }
        if(card.is_enhanced) {
            classes.push('enhanced')
        } 
        if(!houses.includes(card.house)) {
            houses.push(card.house)
        }
        classes.push('house_'+houses.length)
        s += '<div class="'+classes.join(' ')+'">'
        s += gen_card_image(card, 140, 200, 'card_image_card')
        if(card.is_anomaly || card.is_maverick) {
            s += '<img class="house_icon" src="'+unhashThumbImage(
                card.house.substring(0,1).toUpperCase()+
                card.house.substring(1)+'_no_bg.png',
                40
            ) + '">'
        }
        if(card.is_enhanced || card.is_maverick || card.is_anomaly) {
            s += '<div class="infobar">'
            var infos = []
            if(card.is_anomaly) {
                infos.push('Anomaly')
            }
            if(card.is_maverick) {
                infos.push('Maverick')
            }
            if(card.is_enhanced) {
                infos.push('Enhanced')
            }
            if(card.is_legacy) {
                infos.push('Legacy')
            }
            s += infos.join(' ') + '</div>'
        }
        s += '</div>'
    }
    return '<div class="card_images">'+s+'</div>'
}

function gen_rules(data) {
    perform_rule_lookup(data)
    perform_errata_lookup(data)
    return '<div class="deck_errata">Loading errata...</div>'+
        '<div class="deck_rules">Loading rules...</div>'
        
}

function gen_card_combos(data) {
    var cardNames = data.cards.map(function(card){
        return card.card_title
    })
    var combos = cardCombos.filter(function(combo){
        for(var cardName of combo) {
            if(!cardNames.includes(cardName)) {
                return false;
            }
        }
        return true;
    })
    if(combos.length==0) {
        return ''
    }
    return '<div class="deck_combos">'+'<h1>Card Combos</h1>'+
        combos.map(function(combo){
            return combo.map(function(comboCardTitle){
                var card = data.cards.filter(function(deckCard){
                    return deckCard.card_title===comboCardTitle
                })[0]
                return gen_card_image(
                    card,
                    40,
                    60
                ) + card.card_title
            }).join(', ')
        }).join('<br>')
}

var oldSets = ['Call of the Archons', 'Age of Ascension', 'Worlds Collide']

function get_links(data) {
    var d = {
        'Decks of Keyforge': 'https://decksofkeyforge.com/decks/'+data.key,
        'FFG Master Vault': 'https://www.keyforgegame.com/deck-details/'+data.key
    }
    if(oldSets.includes(
        set_name_by_number(data.expansion)
        )
    ){
        d['Aember-forge'] = 'https://aember-forge.com/deck/'+encodeURI(data.name)
    }
    return d
}

function deck_stats(data) {
    return {
        links: get_links(data),
        houses: uniques(data.cards, 'house').map(function(card){
            return card.house
        }),
        actions: data.cards.filter(function(card){
            return card.card_type.match(/action/i)
        }),
        creatures: data.cards.filter(function(card){
            return card.card_type.match(/creature/i)
        }),
        artifacts: data.cards.filter(function(card){
            return card.card_type.match(/artifact/i)
        }),
        upgrades: data.cards.filter(function(card){
            return card.card_type.match(/upgrade/i)
        }),
        rarityCommon: data.cards.filter(function(card){
            return ['Common'].includes(card.rarity)
        }),
        rarityUncommon: data.cards.filter(function(card){
            return ['Uncommon'].includes(card.rarity)
        }),
        rarityRare: data.cards.filter(function(card){
            return ['Rare'].includes(card.rarity)
        }),
        raritySpecial: data.cards.filter(function(card){
            return ['Fixed', 'Variant', 'Special'].includes(card.rarity)
        }),
        rarityEviltwin: data.cards.filter(function(card){
            return ['Evil Twin'].includes(card.rarity)
        }),
        amber: data.cards.reduce(function(total, card) {
            return total + card.amber
        }, 0),
        enhanceAmber: data.cards.reduce(function(total, card) {
            return total + (card.enhance_amber? card.enhance_amber : 0)
        }, 0),
        enhanceDamage: data.cards.reduce(function(total, card) {
            return total + (card.enhance_damage? card.enhance_damage : 0)
        }, 0),
        enhanceCapture: data.cards.reduce(function(total, card) {
            return total + (card.enhance_capture? card.enhance_capture : 0)
        }, 0),
        enhanceDraw: data.cards.reduce(function(total, card) {
            return total + (card.enhance_draw? card.enhance_draw : 0)
        }, 0)
    }
}

function gen_deck_databox(data) {
    var stats = deck_stats(data)
    console.log(stats)
    return '<div class="statbox">'+
        `<div class="stat_set">${set_name_by_number(data.expansion)}</div>`+

        '<div class="stat_houses">'+
        stats.houses.map(function(house){
            return `<img src="${unhashThumbImage(house+'.png', 40)}">`
        }).join(' ')+'</div>'+

        '<div class="stat_types">'+
        `${stats.actions.length} Actions | ${stats.artifacts.length} Artifacts | `+
        `${stats.creatures.length} Creatures | ${stats.upgrades.length} Upgrades`+
        '</div>'+

        Object.keys(stats).filter(function(key) {
            if(!key.match('rarity')) {
                return false;
            }
            return stats[key].length > 0
        }).map(function(key) {
            return `<img src="${images[key]}" width=20> ${key.replace('rarity', '')} ${stats[key].length}`
        }).join(' ')+'</div>'+


        `<div class="stat_amber">${stats.amber} Æmber</div>`+

        '<div class="stat_enhancements">'+
        ['enhanceAmber','enhanceCapture','enhanceDamage','enhanceDraw'].filter(function(enhancement){
            if(oldSets.includes(set_name_by_number(data.expansion))){
                return false;
            }
            return true;
        }).map(function(enhancement){
            return `${stats[enhancement]} <img src="${images[enhancement]}" width="20">`
        }).join(' | ')+'</div>'+

        '<div class="stat_links">'+
        Object.keys(stats.links).map(function(name){
            return `<a href="${stats.links[name]}">${name}</a>`
        }).join('<br>')+'</div>'+
    '</div>'
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
        $(div).append(gen_deck_databox(data))
        $(div).append(gen_rules(data))
        $(div).append(gen_card_combos(data))
        $(div).append(collapsible_block(0, 'Cards', gen_cards(data)))
        $(div)[0].style.display=""
        $('#firstHeading').empty().append(data.name)
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