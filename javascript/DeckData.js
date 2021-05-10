import {getCardImage, updateCardImages, unhashImage, uniques, renderWikitextToHtml, collapsible_block, getLocaleFromSubdomain} from './myutils'
import {cardCombos, images, set_name_by_number} from './data'

var rulingSectionNames = {
  'OutstandingIssues': 'Outstanding Issues',
  'FFGRuling': 'FFG Rulings'
}

var preamble = `
<style>

/* link formatting */
.mw-body a:link {
  text-decoration: none;
  color: #1c2b9c;
  border-bottom: 2px solid transparent;
}

.mw-body a:visited {
  text-decoration: none;
  border-bottom: 2px solid transparent;
  color: #1c2b9c;
}

.mw-body a:hover {
  color: #000000;
  text-decoration: underline;
  border-bottom: 2px solid transparent;
} 

/* decklist preview */
.decklist-viewer {
  display: grid;
  grid-template-columns: auto 150px 150px 150px;
  grid-template-rows: auto 40px 60px auto 40px 50px;
  grid-gap: 5px;
  background-color: #f0f0f0;
  padding: 5px 5px 5px 5px;
  max-width: 850px;
  box-sizing:border-box;
}

.decklist-viewer > div {
  text-align: center;
}

.decklist-image {
  grid-row-start: 1;
  grid-row-end: 7;
  min-width: 200px;
  max-width: 400px;
  padding: 5px 8px 7px 7px;
  margin: 5px;
  border-radius: 3%;
  background-color: #c0c0c0;
}

.decklist-image img {
  max-width: 100%;
  height: auto;
  border-radius: 3%;
  filter: drop-shadow(2px 2px 0px #000000);
}

.decklist-title {
  grid-column-start: 2;
  grid-column-end: 5;
  font-family: castoro;
  font-size: 2.3em;
  line-height: 1em;
  border-bottom: 1px dashed #a0a0a0;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 5px 5px 5px;
}

.set-name {
  grid-column-start: 2;
  grid-column-end: 5;
  font-family: zilla slab;
  font-size: 1.5em;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.set-houses img {
  filter: drop-shadow(3px 3px 0px #303030);
  margin-left: 3px;
  margin-right: 3px;
  height: 40px;
  width: 40px;
}

.set-houses {
  grid-column-start: 2;
  grid-column-end: 5;
  border-bottom: 1px dashed #a0a0a0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.deck-info {
  grid-column-start: 2;
  grid-column-end: 5;
  display: flex;
}

.card-types,
.card-rarities,
.card-enhancements {
  font-family: lato;
  line-height: 2em;
  padding:10px 0px 10px 0px;
  flex:1;
}

.card-types:first-line,
.card-rarities:first-line,
.card-enhancements:first-line {
  font-weight: 500;
  font-family: zilla slab;
  font-size: 1.2em;
  color: #505050;
}

.card-types img,
.card-rarities img,
.card-enhancements img {
  filter: drop-shadow(1px 1px 0px #303030);
  height: 22px;
  width: 22px;
   margin-bottom:2px;
}

.deck-aember {
  grid-column-start: 2;
  grid-column-end: 5;
  font-family: lato;
  border-bottom: 1px dashed #a0a0a0;
  padding: 5px 5px 5px 5px;
}

   .links {
     grid-column-start:2;
     grid-column-end:5;
     display:flex;
   }

.link-1,
.link-2,
.link-3 {
  font-family: lato;
  font-size: 0.9em;
  display: flex;
  flex:1;
  justify-content: center;
  align-items: center;
  padding: 5px 0px 5px 0px;
}

/* organized play record */
.op-results {
  display: grid;
  grid-column-gap: 10px;
  grid-row-gap: 10px;
  max-width: 650px;
  grid-template-columns: auto 200px 100px;
  padding: 0px;
  border-left: 8px solid #e9ebfb;
}

.op-results div {
  padding: 0px;
  font-size: 1em;
  text-align: center;
  font-family: lato;
}

.op-results div:nth-of-type(3n-2) {
  text-align: left;
}

/*other option */

.op-container {
  display: grid;
  max-width: 850px;
  box-sizing:border-box;
  grid-column-gap: 10px;
  grid-row-gap: 10px;
  grid-template-columns: calc(33% - 5px) calc(34% - 5px) calc(33% - 5px);
  padding: 5px;
  
}

.op-event {
  padding: 15px 5px 5px 5px;
  font-size: 1em;
  text-align: center;
  background-color: #fafafa;
  border-radius: 0px;
  font-family: lato;
  line-height: 2em;
  position: relative;
  background-image: linear-gradient(#f0f0f0, #e0e0e0);
}

.op-medal {
  height: 50px;
  width: auto;
  filter: drop-shadow(0px 0px 2px #505050);
}

.laurel {
  height: 150px;
  width: auto;
  margin-top: -30px;
  margin-bottom: -10px;
}

.placement {
  position: absolute;
  top: 20px;
  left: calc(50% - 25px);
  width: 50px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-family: mate sc;
  font-size: 2em;
  line-height: 0.9em;
}

.op-event li {
  display: inline-block;
  margin-right: 3px;
  margin-top: 0px;
  margin-bottom: 0px;
}

.op-event li:first-of-type {
  display: block;
  font-size: 1.2em;
  line-height:1.2em;
  font-family: castoro;
}

/* errata */
dl {
  margin-top: 10px;
}

dt {
  width: 100%;
  font-size: 1.3em !important;
  font-weight: 500;
  box-sizing: border-box;
  background-color: #eaeaea;
  font-weight:500 !important;
  font-family: castoro,lato !important;
  padding: 5px 5px 0px 5px;  

}

dt img {
  height: 56px;
  width: 40px;
  margin-left: 5px;
  margin-right: 10px;
  margin-bottom:5px;
}

dt li {
  list-style:none;
  display:inline-block;
  margin-right:10px;
}

dt a:hover {
  border-bottom:0px !important;
  filter:brightness(.8);
}

.decklist-image a:hover {
  border-bottom:0px !important;
}

/*errata list */
.errata-list dd, .commentary dd {
  background-color: #ffffff;
  font-family: lato; 
  font-size:1em;
  line-height: 1.5em;
  padding: 5px 5px 5px 5px;
  margin: 0px 0px 10px 0px;
}

.errata-list dd:before {
  content: "Should read: ";
  font-style: italic;
  margin-right: 5px;
}

/* faq */
.faq dd, .outstanding-issues dd {
  background-color: #ffffff;
  font-family: lato;
  font-size:1em;
  line-height: 1.5em;
  margin: 0px 0px 0px 0px;
}

.faq dd:nth-of-type(2n), .outstanding-issues dd:nth-of-type(2n) {
    border-bottom:1px dashed #a0a0a0;
    padding: 0px 5px 10px 5px; 
}

.faq dd:nth-of-type(2n-1), .outstanding-issues dd:nth-of-type(2n-1) {
    padding: 10px 5px 5px 5px; 
  
}

.faq dd:nth-of-type(2n-1):before, .outstanding-issues dd:nth-of-type(2n-1):before {
  content:"Q: ";
  font-size:1.3em;
  font-family:castoro;
  margin:3px 5px 0px 0px;
}

.faq dd:nth-of-type(2n):before {
  content:"A: ";
  font-size:1.3em;
  font-family:castoro;
    margin:1px 5px 0px 0px;
}

.commentary dd:first-of-type {
   padding: 10px 5px 5px 5px; 
}

.commentary dd+dd {
    border-top:1px dashed #a0a0a0;
    padding: 15px 5px 5px 5px; 
}

.outstanding-issues dd:nth-of-type(2n):before {
  content:"Arcana Advises: ";
  font-size:1.2em;
  font-family:castoro;
    margin:1px 5px 0px 0px;
}

.faq dd:last-of-type, .outstanding-issues dd:last-of-type {
  border-bottom:0px;
}


/* outstanding issues */
.outstanding-issues-disclaimer {
  font-family:lato;
  font-size:1em;
  line-height:1.5em;
  margin-bottom:20px; 
}

@media screen and (min-width:901px) {
.mw-body h2 {
  font-family: castoro !important;
  border-bottom:1px solid #000000 !important;
}

.mw-body h2:after {
  border:0px solid #000000 !important;
}

}

@media screen and (max-width: 900px) {

  .mw-body h2 {
  font-family: castoro !important;
  border-bottom:1px solid #000000 !important;
  }

  .mw-body h2:after {
  border:0px solid #000000 !important;
  }


  .decklist-viewer {
    display: grid;
    grid-template-columns: calc(33% - 2px) calc(33% - 3px) calc(33% - 2px);
    grid-gap: 5px;
    background-color: #ffffff;
    padding: 5px 5px 5px 5px;
    max-width: 850px;
    border:0px;
  }

  .decklist-image {
    grid-column-start: 1;
    grid-column-end: 4;
    min-width: 250px;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
    text-align:center;
    padding: 0px;
    background-color:#ffffff;
  }

  .decklist-title {
    grid-column-start: 1;
    grid-column-end: 4;
    font-size: 1.8em;
    line-height: 1em;
    padding: 10px 5px 5px 5px;
  }

  .set-name {
    grid-column-start: 1;
    grid-column-end: 4;
    font-size: 1.3em;
  }

  .set-houses {
    grid-column-start: 1;
    grid-column-end: 4;
    border-bottom: 1px dashed #a0a0a0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 0px 0px 10px 0px;
  }
  .deck-info {
    grid-column-start: 1;
    grid-column-end: 4;
  } 

   .card-types, .card-rarities, .card-enhancements {
      padding:0px 0px 10px 0px;
  }

  .card-types:first-line,
  .card-rarities:first-line,
  .card-enhancements:first-line {
    font-size: 1em;
    font-family: lato;
    font-weight:600;
  }

  .deck-aember {
    grid-column-start: 1;
    grid-column-end: 4;
    padding: 10px 5px 10px 5px;
  }
   

   .links {
     grid-column-start:1;
     grid-column-end:4;
   }

  .link-1,
  .link-2,
  .link-3 {
    font-size: 0.9em;
    padding: 5px 0px 5px 0px;
  }

  .op-container {
    grid-template-columns: calc(50% - 5px) calc(50% - 5px);
  }

  dt li {
    display:block;
  }

  
  dt img {
        height: 42px;
    width: 30px;
  }

}

/* adjustments for very small screens */
@media screen and (max-width:370px) {
  
  .deck-info {
     display:block;
  }

  .card-types,
  .card-rarities,
  .card-enhancements {
    grid-column-start: 1;
    grid-column-end: 4;
    border-bottom:1px dashed #a0a0a0;
  }

    .op-container {
    grid-template-columns: 100%;
  }

  .deck-aember {
    grid-column-start: 1;
    grid-column-end: 4;
    padding: 0px 0px 5px 0px;
  }


}



/* 
 *
 * Formatting for the card list preview
 *
 */

  .card-preview-gallery {
    width: 100%;
    overflow: hidden;
    display: flex; /* I hate internet explorer */
    flex-wrap: wrap;
    display: grid; /* every other browser gets a pretty grid */
    grid-column-gap:10px;
    grid-row-gap:10px;
  }

.card-preview {
  position: relative;
    min-width: 150px;
    max-width: 300px;
    overflow: hidden;
    height: auto;
  transition:all .5s ease-in-out;
  }

.card-preview:hover {
   filter:brightness(.8);
   cursor:pointer;
}

  .card-preview img {
    width: 100%;
    height: auto;
  }


.enhanced-card {
  position:absolute;
  height:100%;
  width:100%;
  display:block;
  top:0px;
  left:0px;
  content:"";
  z-index:5;
  opacity:1;
  border-radius:5%;
}

.enhanced-card:before {
  position:absolute;
  top:40%;
  right:0px;
  content:"Enhanced";
  font-family:lato;
  padding:3px 5px 3px 10px;
  background-color:#353331;
  color:white;
  opacity:1;
  font-size:.9em;
}

@media screen and (max-width:600px) {
  .card-preview-gallery {
    grid-template-columns: repeat(2, 1fr);
    grid-column-gap:5px;
    grid-row-gap:5px;
  }

  .enhanced-card:before {
  font-size:.85em;
  }

}

@media screen and (min-width: 601px) and (max-width: 900px) {
  .card-preview-gallery {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (min-width: 901px) and (max-width: 1200px) {
  .card-preview-gallery {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media screen and (min-width: 1201px) {
  .card-preview-gallery {
    grid-template-columns: repeat(5, 1fr);
  }

}

.maverick-brobnar, .maverick-dis, .maverick-logos, .maverick-mars, .maverick-sanctum, .maverick-star-alliance, .maverick-saurian, .maverick-shadows, .maverick-untamed, .maverick-unfathomable {
  height: 20%;
  width: 30%;
  position: absolute;
  top: 0px;
  left: 0px;
  display: block;
  filter:drop-shadow(2px 2px 3px #303030);
}

.maverick-card {
  position: absolute;
  top: 0px;
  right: 0px;
  display: block;
  height: 22%;
  width: 30%;
  opacity: 1;
}

.legacy-card {
  position: absolute;
  bottom: 2%;
  right: 1%;
  display: block;
  height: 18%;
  width: 18%;
  filter: drop-shadow(1px 1px 1px #505050) brightness(0.9);
}


/* CSS FOR MEDIA COMMONS */

.maverick-brobnar {
    content: url(https://archonarcana.com/images/3/35/Maverick-brobnar-amber.png);
}

.maverick-dis { 
  content:url(https://archonarcana.com/images/0/0d/Maverick-dis-amber.png);
}

.maverick-logos {
  content:url(https://archonarcana.com/images/b/b6/Maverick-logos-amber.png);
}

.maverick-mars { 
  content:url(https://archonarcana.com/images/5/58/Maverick-mars-amber.png);
}

.maverick-sanctum  { 
  content:url(https://archonarcana.com/images/e/e1/Maverick-sanctum-amber.png);
}

.maverick-saurian  { 
  content:url(https://archonarcana.com/images/7/75/Maverick-saurian-amber.png);
}

.maverick-shadows  { 
  content:url(https://archonarcana.com/images/a/a5/Maverick-shadows-amber.png);
}

.maverick-star-alliance  { 
  content:url(https://archonarcana.com/images/7/7f/Maverick-staralliance-amber.png);
}

.maverick-untamed  { 
  content:url(https://archonarcana.com/images/5/5a/Maverick-untamed-amber.png);
}

.maverick-card {
  content: url(https://archonarcana.com/images/a/a0/Maverick-corner.png);
}

.legacy-card {
  content: url(https://archonarcana.com/images/d/d1/Legacy-orange.png);
}
</style>

<!-- import fonts -->
  <link href='https://fonts.googleapis.com/css?family=Castoro' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css?family=Mate SC' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css?family=Lato' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css?family=Zilla Slab' rel='stylesheet'>
`

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
                for(var section of ['FAQ', 'FFGRuling', 'Commentary', 'OutstandingIssues']) {
                  write_rules(
                    data.cargoquery.map(function(result) {
                        return result.title
                    }),
                    deckdata.cards,
                    section
                  )
                }
            }
        }
    )
}

`https://archonarcana.com/api.php?action=cargoquery&
format=json&
tables=Event%2C%20EventResults&
fields=EventResults.DeckID%2C%20EventResults.Rank%2C%20Event.Name%2C%20Event.Format&
join_on=EventResults.Name%3DEvent.Name`
function perform_event_lookup(deckdata) {
  var base = '/api.php?action=cargoquery&format=json'
  var params = [
      'tables=EventResults, Event',
      'fields=EventResults.Name, EventResults.Rank, Event.Format, Event.Variant',
      'join_on=EventResults.Name=Event.Name',
      `where=EventResults.DeckID="${deckdata.key}"`,
      'limit=500'
  ]
  var url = encodeURI(base+'&'+params.join('&'))
  $.ajax(
    url,
    {
        success: function (data, status, xhr) {
            $('.deck_events').empty()
            write_events(
                data.cargoquery.map(function(result) {
                    return result.title
                })
            )
        }
    })
}

var event_images = {
  '1': '<img src="https://archonarcana.com/images/3/3f/Noun_Laurel_Wreath_314748_gold.png" class="laurel" alt="Golden victory laurel">',
  '2': '<img src="https://archonarcana.com/images/3/34/Noun_Laurel_Wreath_314748_silver.png" class="laurel" alt="Silver victory laurel">',
  'Top 4': '<img src="https://archonarcana.com/images/d/d6/Noun_Laurel_Wreath_314748_olive.png" class="laurel" alt="Green victory laurel">',
  'Top 8': '<img src="https://archonarcana.com/images/6/62/Noun_Laurel_Wreath_314748.png" class="laurel" alt="Black victory laurel">',
  'Top 16': '<img src="https://archonarcana.com/images/6/62/Noun_Laurel_Wreath_314748.png" class="laurel" alt="Black victory laurel">'
}
var event_text = {
  '1': '1st',
  '2': '2nd',
  'Top 4': 'top 4',
  'Top 8': 'top 8',
  'Top 16': 'top 16'
}
function write_events(cargo_results) {
  if(cargo_results.length==0) {
    return
  }
  var div = $('.deck_events')
  var s = `
  <div class="op-container">
  ${
    cargo_results.map(function(placement) {
      return `<div class="op-event">
      ${event_images[placement.Rank]}
      <span class="placement">${event_text[placement.Rank]}</span>
      <li><a href="${
        placement.Name.match('Grand Championship') ? 'Grand_Championships' :
        placement.Name
      }">${placement.Name}</a>
      <li>${placement.Format} ${placement.Variant}
      </div>`
    }).join('\n')
  }
  </div>
  `
  div.append(collapsible_block('h2', 'Organized Play', s, 1))
}

function perform_errata_lookup(deckdata) {
    var base = '/api.php?action=cargoquery&format=json'
    var params = [
        'tables=ErrataData',
        'fields=ErrataData.Text, CONCAT(_pageTitle)=title',
        'where=Tag="latest" OR Version<>""',
        'order by="ErrataData._ID DESC"',
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
        if (result['RulesType']==='OutstandingIssues' && !result['RulesText'].includes('//')){
            return false;
        }
        if (
            (
                ((result['RulesText'] && result['RulesText'].includes(name)) && !result['RulesPages']) ||
                ((result['RulesPages'] && result['RulesPages'].includes('•'+name+'•')))
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
        if(texts_by_card_list[card_list]) {
            texts_by_card_list[card_list].push(result)
        } else {
            texts_by_card_list[card_list] = [result]
        }
    }
    return texts_by_card_list
}

function write_errata(cargo_results, cards) {
    var written = {}
    var div = $('.deck_errata')
    var errata_text = ''
    for(var card of cards) {
        for(var result of cargo_results) {
            if(written[card.card_title]){
              continue
            }
            if(result.title === card.card_title) {
                written[card.card_title] = true
                errata_text += '<dt>'
                errata_text += '<li>' + gen_rule_card_image(card, 40, 60)+card.card_title + '</li>'
                errata_text += '</dt>'
                errata_text += '<dd>'
                errata_text += renderWikitextToHtml(result.Text)
                errata_text += '</dd>'
            }
        }
    }
    if(errata_text){
      errata_text = `
      <dl class="errata-list">
      ${errata_text}
      </dl>
      `
      div.append(collapsible_block('h2', 'Errata', errata_text, 2))
    }
}

var outstanding_issue_disclaimer = `<div class="outstanding-issues-disclaimer">We recommend speaking with the head judge before an event to find out how they will rule on the following ambiguous rules interactions. Arcana Advises is a recommendation on how to resolve each outstanding issue in the absence of a judge. For more information, <a href="https://archonarcana.com/Outstanding_Issues">click here</a>.</div>`
function write_rules(cargo_results, cards, section) {
    var texts = correlate_rules_by_card(cargo_results, cards, section)
    if(Object.keys(texts).length==0) {
        return
    }
    var div = $('.deck_rules')
    var s = ''
    var dl_class = 'faq'
    if(section==="Commentary") {
        dl_class = 'commentary'
    } else if (section==="OutstandingIssues") {
        dl_class = 'outstanding-issues'
    }
    //div.append('<h1>'+section+'</h1><br>')
    for(var card_set of Object.keys(texts).sort()) {
        var rule_text = `
        ${section==='OutstandingIssues'? outstanding_issue_disclaimer : ''}
        <dl class="${dl_class}">
        <dt>
        ${texts[card_set][0]['cards'].map(
            function(card) {
                return `<li>${gen_rule_card_image(card, 40, 60)+card.card_title}</li>`
            }
        ).join('')}
        </dt>
        `
        for(var result of texts[card_set]) {
            if(!result['RulesText']){
              continue
            }
            var q_a = result['RulesText'].split('//')
            rule_text += q_a.map(function(text) {
                return `<dd>${renderWikitextToHtml(
                  (texts[card_set][0]['cards'].length==1) ? text.replace(
                    /this card/g, 
                    `[[${texts[card_set][0]['cards'][0].card_title}]]`
                   ) : text
                )}</dd>`
            }).join('\n')
        }
        rule_text += '</dl>'
        s += rule_text
    }
    div.append(collapsible_block(
      'h2', 
      section in rulingSectionNames? rulingSectionNames[section] : section,
      s,
      3))
    //div.append(collapsible_block(0, section, s))
}

function gen_deck_image(data) {
    var lang = Object.keys(mw.language.data)[0]
    if(!['en','es','it','de','fr','pl','pt','th','zh'].includes(lang)) {
        lang = 'en'
    }
    var src = `https://images.skyjedi.com/custom/${data.key}/${lang}/deck_list.png`
    return `
    <div class="decklist-image">
    <a href="${src}"><img src="${src}" alt="Archon Card"></a>
    </div>`
}

function gen_rule_card_image(card, width, height) {
    return `<a href="/${card.card_title}">${getCardImage(card, {width:200, noFullUpdate:true})}</a>`
}

function gen_card_gallery_image(card) {
  var maverick = card.is_maverick? `<div class="maverick-card"></div>`: ''
  var enhanced = card.is_enhanced? `<div class="enhanced-card"></div>` : ''
  var anomaly = card.is_anomaly? `<div class="anomaly-card"></div>` : ''
  var legacy = card.is_legacy? `<div class="legacy-card"></div>` : ''
  var houseicon = (card.is_anomaly || card.is_maverick) ? `<div class="maverick-${card.house.toLowerCase()}"></div>` : ''
  var s = `<div class="card-preview">
<a href="/${card.card_title}">
${getCardImage(card, {width: 200, splitGigantic: true})}
${houseicon}
${maverick}
${enhanced}
${anomaly}
${legacy}
</a></div>`
  return s
}

function gen_cards(data) {
  var s = ''
  for(var card of data.cards) {
      s += gen_card_gallery_image(card)
  }
  return collapsible_block('h2', 'Cards', 
    '<div class="card-preview-gallery">'+s+'</div>', 4)
}

function gen_events(data) {
  perform_event_lookup(data)
  return '<div class="deck_events">Loading events...</div>'
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
                return gen_rule_card_image(
                    card,
                    40,
                    60
                ) + card.card_title
            }).join(', ')
        }).join('<br>')
}

var oldSets = ['Call of the Archons', 'Age of Ascension', 'Worlds Collide']

function get_links(data) {
    var d = [
      ['Master Vault', 'https://www.keyforgegame.com/deck-details/'+data.key],
      ['Decks of KeyForge', 'https://decksofkeyforge.com/decks/'+data.key]
    ]
    if(oldSets.includes(
        set_name_by_number(data.expansion)
        )
    ){
        d.push(['Æmber-Forge', 'https://aember-forge.com/deck/'+encodeURI(data.name)])
    }
    return d
}

function deck_stats(data) {
    return {
        links: get_links(data),
        houses: uniques(data.cards, 'house').map(function(card){
            return card.house
        }).filter(function(house){
            return house !== 'The Tide'
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
    var enhancements = !oldSets.includes(set_name_by_number(data.expansion)) ? 
        ['enhanceAmber','enhanceCapture','enhanceDamage','enhanceDraw'] :
        false
    var houses = stats.houses.map(function(house){
        return `<img src="${unhashImage(house.replace(/ /g,'_')+'.png')}" alt="${house} icon">`
    }).join('\n')
    var rarities = Object.keys(stats).filter(function(key) {
        if(!key.match('rarity')) {
            return false;
        }
        return !key.match('Eviltwin') || stats[key].length > 0
    }).map(function(key) {
        return `${stats[key].length} <img src="${images[key]}" width=20 alt="${key.replace('rarity', '')}">`
    }).join('<br>')
    var s = `
    <div class="decklist-viewer">
      ${gen_deck_image(data)}
      <div class="decklist-title">${data.name}</div>
      <div class="set-name">${set_name_by_number(data.expansion)}</div>
      <div class="set-houses">${houses}</div>
      <div class="deck-info">
          <div class="card-types">
          Card Types<br>
          ${stats.actions.length} Actions<br>
          ${stats.artifacts.length} Artifacts<br>
          ${stats.creatures.length} Creatures<br>
          ${stats.upgrades.length} Upgrades
          </div>
          <div class="card-rarities">Card Rarities<br>${rarities}</div>
          ${enhancements ? `<div class="card-enhancements">
              Enhancements<br>
              ${enhancements.map(function(enhancement){
                  return `${stats[enhancement]} <img src="${images[enhancement]}" width="20">`
              }).join('<br>')}
          </div>` : ''}
      </div>
      <div class="deck-aember">${stats.amber}  Æmber</div>
      <div class="links">
      ${
          stats.links.map(function(item, n){
              return `<div class="link-${n+1}">
              <a href="${item[1]}">${item[0]}</a>
              </div>`
          }).join('\n')
      }
      </div>
    </div>`
    return collapsible_block('h2', 'Decklist', s, 0)
}

function write_deck_data(data) {
    $('title').empty().append(data.name)
    $('.noarticletext').replaceWith('')
    var div = $('#bodyContent') //$('.deck_contents')
    $(div).empty()
    $(div).append(preamble)
    $(div).append(gen_deck_databox(data))
    $(div).append(gen_events(data))
    $(div).append(gen_rules(data))
    $(div).append(gen_card_combos(data))
    $(div).append(gen_cards(data))
    //$(div)[0].style.display=""
    $('#firstHeading').empty().append(data.name)
    updateCardImages()
}

function read_wiki_deck_data() {
    var divs = $('.deckjson')
	divs.map(function(id){
        var div = divs[id]
        write_deck_data(
            JSON.parse($(div).text())
        )
    })
}

function pull_deck_data(deck_key) {
    var locale = getLocaleFromSubdomain()
    $.ajax(
        'https://keyforge.tinycrease.com/get_aa_deck_data?key='+deck_key+'&locale='+locale,
        {
            success: function (deck, status, xhr) {
                write_deck_data(deck)
            },
            error: function (xhr, status, thrownError) {
                $('title').empty().append("404: Deck not found in Master Vault")
                $('#mw-content-text').empty().append("<h2>404 - Deck Not Found</h2>").append(
                  "This deck is not available on Archon Arcana. Please double check that the ID is correct. If you recently scanned this deck into the Master Vault, you may need to wait 5 minutes and try again."
                )
            }
        }
    )
}

function gen_deck_data() {
    var noarticle = $('.noarticletext')
    var content = $('#mw-content-text')
    var title = mw.config.values.wgTitle
    var ns = mw.config.values.wgNamespaceNumber
    if(ns != mw.config.values.wgNamespaceIds['deck']) {
        return
    }
    var deck_key = title.toLowerCase()
    content.append('<div class="deck_contents"></div>')
    pull_deck_data(deck_key)
}

export {gen_deck_data}