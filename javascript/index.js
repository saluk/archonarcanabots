import {init_cargo_search2, CSearch} from './CargoSearch'
import {replace_charts} from './chart_with_js'
import {choose_random_cards} from './randomcard'
import {init_deck_search} from './DeckSearch'
import {gen_deck_data} from './DeckData'
import {carousel} from './myutils'
import './share42.js' // share42 sharing module
import {hookTopSearch} from './TopSearch.js'
import {deck_counts} from './deck_counts.js'

var arcana_main = function() {
	hookTopSearch()
	deck_counts()
	choose_random_cards()
	carousel(true)
	init_cargo_search2()
	gen_deck_data()
	init_deck_search()
	replace_charts()
}

arcana_main()
export {arcana_main}