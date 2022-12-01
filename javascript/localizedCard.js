import {parseQueryString, pageTitle, to_full} from './myutils'
import {dumb_locale_menu} from './localization'

function loadLocalizedCard(cardname, locale) {
    var el = $('#bodyContent')
    el.empty()
    $.ajax(`/api.php?action=parse&format=json&text=%7B%7B%23invoke%3A%20luacard%7Cviewcard%7Ccardname%3D${cardname}%7Clocale%3D${locale}%7D%7D`,
      {
        success: function (data, status, xhr) {
          var text = data.parse.text['*']
          el.append(text)
          $('#firstHeading').empty()
          $('#firstHeading').append($('localetitle')[0].innerText)
          document.title = $('localetitle')[0].innerText
          dumb_locale_menu()
        },
        error: function(req, status, error) {
          el.append('<div>Error loading localized card</div>')
        }
      }
    )
}

function renderLocalizedCard() {
    var cardLocalization = parseQueryString('cardLocale')
    var cardEntry = $('.cardEntry')
    var title = pageTitle()
    console.log(cardEntry)
    if(cardEntry){
      cardLocalization = cardEntry.attr('data-locale') || cardLocalization
      title = cardEntry.attr('data-name') || title
      console.log(title)
      console.log(cardLocalization)
      if (cardLocalization) {
        loadLocalizedCard(title, to_full(cardLocalization))
      }
    }
}

export {renderLocalizedCard}
