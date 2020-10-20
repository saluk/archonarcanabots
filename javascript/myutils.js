var parseQueryString = function (argument) {
	var res = '[\\?&]' + argument + '=([^&#]*)'
	var found = new RegExp(res).exec(window.location.href)
	if (found) {
	  return decodeURIComponent(found[1])
	} else {
	  return ''
	}
  }

function htmlDecode(input){
	var e = document.createElement('div');
	e.innerHTML = input;
	return e.childNodes[0].nodeValue;
  }

function uniques(objects, unique_field) {
	var unique = []
	var fields = []
	for(var ob of objects) {
		if(!fields.includes(ob[unique_field])) {
			unique.push(ob)
			fields.push(ob[unique_field])
		}
	}
	return unique
}

var unhashImage = function(imgName) {
	var hash = md5(imgName)
	var firsthex = hash.substring(0,1)
	var first2 = hash.substring(0,2)
	return '/images/'+firsthex+'/'+first2+'/'+imgName
}
  
var unhashThumbImage = function(imgName) {
	return 'https://archonarcana.com/thumb.php?f='+imgName+'&width=200'
}

function isElementInViewport (el) {

	// Special bonus for those using jQuery
	if (typeof jQuery === "function" && el instanceof jQuery) {
		el = el[0];
	}
  
	var rect = el.getBoundingClientRect();
  
	return (
		rect.top >= 0 &&
		rect.left >= 0 &&
		rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
		rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
	);
}

function renderWikitextToHtml(text) {
	var s = htmlDecode(text)
	// Split "//"
	s = s.replace('//', '<br>')
	// Links
	s = s.replace(/\[\[.*?\]\]/g, function (link) {
		var linktext = link.slice(2, link.length-2)
		var linkparts = linktext.split('|')
		var linksource = linkparts[0]
		var linkname = linksource
		if(linkparts[1]) {
			linkname = linkparts[1]
		}
		return '<a href="/'+linksource+'">'+linkname+'</a>'
	})
	// Numbered list tags
	var lines = s.split('\n')
	var ol = false
	for(var i in lines) {
		var line = lines[i]
		// TODO Iterate through lines inserting <ol> where a line starts with '#' and </ol> where
		// the line stops. At the end, if we were in an ol section, add /ol
		if(!ol && line.startsWith('#')) {
			ol = true
			lines[i] = '<ol><li>' + line.substring(1) + '</li>'
		} else if (ol && line.startsWith('#')) {
			lines[i] = '<li>'+line.substring(1)+'</li>'
		} else if (ol && !line.startsWith('#')) {
			ol = false
			lines[i] = '</ol>'
		} else if (i<lines.length-1) {
			lines[i] = line + '\n'
		}
	}
	if(ol) {
		lines.push('</ol>')
	}
	s = lines.join('')
	// Replace newlines
	s = s.replace(/\n+/g,'<br>')
	return s
}

export {parseQueryString, unhashImage, unhashThumbImage, renderWikitextToHtml,
	isElementInViewport, htmlDecode, uniques}