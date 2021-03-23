//import {replace_charts} from './chart_with_js'
import {gen_deck_data} from './DeckData'
import './share42.js' // share42 sharing module

var arcana_main = function() {
	gen_deck_data()
	replace_charts()
}

arcana_main()
export {arcana_main}