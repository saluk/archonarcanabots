$.when(
    mw.loader.getScript( '/index.php?title=MediaWiki:Dplsearch.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript( '/index.php?title=MediaWiki:CargoSearch.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript( '/index.php?title=MediaWiki:jquery-endless-scroll.js&action=raw&ctype=text/javascript')
)
	.then(function() {
		console.log("loaded external js");
        init_dpl_search(10);
        init_cargo_search();
});