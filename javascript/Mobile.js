var parseQueryString = function (argument) {
	var res = '[\\?&]' + argument + '=([^&#]*)'
	var found = new RegExp(res).exec(window.location.href)
	if (found) {
	  return decodeURIComponent(found[1])
	} else {
	  return ''
	}
}

$.when(
    mw.loader.getScript('https://cdnjs.cloudflare.com/ajax/libs/blueimp-md5/2.16.0/js/md5.min.js'),
    mw.loader.getScript('https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.min.js')
)
	.then(function() {
        if(parseQueryString('testjs')==='true') {
            mw.loader.getScript('/index.php?title=MediaWiki:<FILENAMEDEBUG_main.js>&action=raw&ctype=text/javascript')
        } else {
            //mw.loader.getScript('/index.php?title=MediaWiki:<FILENAME_main.js>&action=raw&ctype=text/javascript')
        }
});
