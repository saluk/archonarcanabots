$.when(
    mw.loader.getScript( '/index.php?title=MediaWiki:CargoSearch.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript( '/index.php?title=MediaWiki:jquery-endless-scroll.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript( 'https://cdnjs.cloudflare.com/ajax/libs/blueimp-md5/2.16.0/js/md5.min.js')
)
	.then(function() {
		console.log("loaded external js");
        init_cargo_search();
});