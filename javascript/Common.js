// Gadgets:

//syntax highlighter
mw.loader.load('//www.mediawiki.org/w/index.php?title=MediaWiki:Gadget-DotsSyntaxHighlighter.js&action=raw&ctype=text/javascript');


$.when(
    mw.loader.getScript( '/index.php?title=MediaWiki:CargoSearch.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript( '/index.php?title=MediaWiki:jquery-endless-scroll.js&action=raw&ctype=text/javascript')
)
	.then(function() {
		console.log("loaded external js");
        init_cargo_search();
});

