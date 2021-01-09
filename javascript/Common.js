var parseQueryString = function (argument) {
	var res = '[\\?&]' + argument + '=([^&#]*)'
	var found = new RegExp(res).exec(window.location.href)
	if (found) {
	  return decodeURIComponent(found[1])
	} else {
	  return ''
	}
  }

// Gadgets:

//syntax highlighter
mw.loader.load('//www.mediawiki.org/w/index.php?title=MediaWiki:Gadget-DotsSyntaxHighlighter.js&action=raw&ctype=text/javascript');

$.when(
    mw.loader.getScript('https://cdnjs.cloudflare.com/ajax/libs/blueimp-md5/2.16.0/js/md5.min.js'),
    mw.loader.getScript('https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.min.js')
)
	.then(function() {
})

