//import {replace_charts} from './chart_with_js'
import {choose_random_cards} from './randomcard'
import {carousel} from './myutils'
import './share42.js' // share42 sharing module
import {hookTopSearch} from './TopSearch'
import {deck_counts} from './deck_counts'
import {show_translations, dumb_locale_menu} from './localization'

var arcana_main = function() {
	show_translations()
	dumb_locale_menu()
	hookTopSearch()
	deck_counts()
	choose_random_cards()
	carousel(true)
//	replace_charts()
}

arcana_main()
export {arcana_main}