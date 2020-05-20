// Gadgets:

//syntax highlighter
mw.loader.load('//www.mediawiki.org/w/index.php?title=MediaWiki:Gadget-DotsSyntaxHighlighter.js&action=raw&ctype=text/javascript');

$.when(
    mw.loader.getScript('/index.php?title=MediaWiki:CargoSearch.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript('/index.php?title=MediaWiki:jquery-endless-scroll.js&action=raw&ctype=text/javascript'),
    mw.loader.getScript('https://cdnjs.cloudflare.com/ajax/libs/blueimp-md5/2.16.0/js/md5.min.js'),
    mw.loader.getScript('https://cdn.jsdelivr.net/npm/select2@4.0.13/dist/js/select2.min.js')
)
	.then(function() {
        console.log("loaded external js")
        init_cargo_search()
})

