import {init_cargo_search2, CSearch} from './CargoSearch'
import {hookTopSearch} from './TopSearch.js'

var arcana_main = function() {
	hookTopSearch()
	init_cargo_search2()
}

arcana_main()
export {arcana_main}