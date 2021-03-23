import {choose_random_cards} from './randomcard'
import {carousel} from './myutils'
import './share42.js' // share42 sharing module
import {deck_counts} from './deck_counts'
import {show_translations, dumb_locale_menu} from './localization'

var arcana_main = function() {
	show_translations()
	dumb_locale_menu()
	deck_counts()
	choose_random_cards()
	carousel(true)
}

arcana_main()
export {arcana_main}