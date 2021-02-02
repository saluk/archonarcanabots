import {replace_charts} from './chart_with_js'
import {choose_random_cards} from './randomcard'
import {carousel} from './myutils'
import './share42.js' // share42 sharing module
import {hookTopSearch} from './TopSearch.js'
import {deck_counts} from './deck_counts.js'
import {parseQueryString} from './myutils'

function show_translations() {
	var locale;
	locale = parseQueryString('locale')
	if(!locale)
		locale = mw.config.get('wgUserLanguage')
	$('.translate-'+locale).css('display','inline')
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