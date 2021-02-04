import {replace_charts} from './chart_with_js'
import {choose_random_cards} from './randomcard'
import {carousel} from './myutils'
import './share42.js' // share42 sharing module
import {hookTopSearch} from './TopSearch.js'
import {deck_counts} from './deck_counts.js'
import {getLocale} from './myutils'

function show_translations() {
	$('.translate-'+getLocale()).css('display','inline')
}

var arcana_main = function() {
	hookTopSearch()
	deck_counts()
	choose_random_cards()
	carousel(true)
	replace_charts()
	show_translations()
}

arcana_main()
export {arcana_main}