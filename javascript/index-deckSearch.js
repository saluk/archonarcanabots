import {init_deck_search} from './DeckSearch'
import {hookTopSearch} from './TopSearch.js'

var arcana_main = function() {
	hookTopSearch()
	init_deck_search()
}

arcana_main()
export {arcana_main}