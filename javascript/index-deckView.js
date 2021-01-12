import {replace_charts} from './chart_with_js'
import {gen_deck_data} from './DeckData'
import './share42.js' // share42 sharing module
import {hookTopSearch} from './TopSearch.js'

var arcana_main = function() {
	hookTopSearch()
	gen_deck_data()
	replace_charts()
}

arcana_main()
export {arcana_main}