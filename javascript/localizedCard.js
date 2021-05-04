import {parseQueryString, pageTitle} from './myutils'

function loadLocalizedCard(cardname, locale) {
    $.ajax(`https://archonarcana.com/api.php?action=parse&format=json&text=%7B%7B%23invoke%3A%20luacard%7Cviewcard%7Ccardname%3D${cardname}%7Clocale%3D${locale}%7D%7D`,
      {
        success: function (data, status, xhr) {
          var text = data.parse.text['*']
          $('.mw-parser-output').replaceWith(text)
        },
        error: function(req, status, error) {
          $('.mw-parser-output').append('<div>Error loading localized card</div>')
        }
      }
    )
}

function renderLocalizedCard() {
    var cardLocalization = parseQueryString('cardLocale')
    var title = pageTitle()
    if(cardLocalization && $('.cardEntry')){
        loadLocalizedCard(title, cardLocalization)
    }
}

export {renderLocalizedCard}