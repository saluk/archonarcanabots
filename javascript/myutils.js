var parseQueryString = function (argument) {
	var res = '[\\?&]' + argument + '=([^&#]*)'
	var found = new RegExp(res).exec(window.location.href)
	if (found) {
	  return decodeURIComponent(found[1])
	} else {
	  return ''
	}
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

export {parseQueryString, unhashImage, unhashThumbImage, isElementInViewport}