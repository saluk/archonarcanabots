import {init_cargo_search2, CSearch} from './CargoSearch'
import {replace_charts} from './chart_with_js'
import {choose_random_cards} from './randomcard'
import {init_deck_search} from './DeckSearch'
import {gen_deck_data} from './DeckData'

var arcana_main = function() {
	console.log("hello")
	gen_deck_data()
	init_cargo_search2()
	replace_charts()
	choose_random_cards()
	init_deck_search()
	console.log(CSearch)
}

arcana_main()
export {arcana_main}