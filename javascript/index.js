import {init_cargo_search2, CSearch} from './CargoSearch'
import {replace_charts} from './chart_with_js'
import {choose_random_cards} from './randomcard.js'

var arcana_main = function() {
	console.log("hello")
	init_cargo_search2()
	replace_charts()
	choose_random_cards()
	console.log(CSearch)
}

arcana_main()
export {arcana_main}