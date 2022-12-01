import {multiHouseCards} from './data.js'
const md5 = require('md5')

var parseQueryString = function (argument) {
	var res = '[\\?&]' + argument + '=([^&#]*)'
	var found = new RegExp(res).exec(window.location.href)
	if (found) {
	  return decodeURIComponent(found[1])
	} else {
	  return ''
	}
  }

var pageTitle = function() {
	return decodeURIComponent(window.location.href.match(/\/\/.*?\/(.*?)($|\#|\?)/)[1]).replace(/\_/g, ' ')
}

var locales = {
	"en": [["en", "English"]],
	"pt-pt": [["pt-br", "Português do Brasil"], ["pt", "português"]],
	"it-it": [["it", "Italiano"]],
	"zh-hant": [["zh-hant", "中文（繁體）"], ["zh-tw", "中文（台灣）"]],
	"de-de": [["de", "Deutsch"], ["de-formal", "Deutsch (Sie-Form)"]],
	"zh-hans": [["zh", "中文"], ["zh-hans", "中文（简体）"]],
	"th-th": [["th", "ไทย"]],
	"ko-ko": [["ko", "한국어"], ["ko-kp", "조선말"]],
	"pl-pl": [["pl", "Polski"]],
	"fr-fr": [["fr", "Français"], ["frc", "français cadien"]],
	"es-es": [["es", "Español"]],
	'ru-ru': [['ru', "Pусский"]]
}

function getLocaleFromSubdomain() {
	var host = window.location.host
	var subdomain = host.split('.')[0]
	if(subdomain === 'www' || subdomain === 'archonarcana') {
		return 'en'
	}
	return to_full(subdomain)
  }

function getLocale(){
	var locale;
	var subdomain = window.location.hostname.split('\.')[0]
	locale = parseQueryString('locale')
	if(!locale && subdomain !== 'www' && subdomain !== 'archonarcana') {
		locale = subdomain
	} else if(!locale) {
		locale = mw.config.get('wgUserLanguage')
	}
	var full = to_full(locale)
	if(full=='en') return 'en'
	return locale
}

function to_full(locale) {
	for(const [loc, val] of Object.entries(locales)) {
		function has_locale(locale) {
			return function(item) {
				return item[0] == locale
			}
		}
		if(val.filter(has_locale(locale)).length>0){
			return loc
		}
	}
	return 'en'
}

function getFullLocale() {
	var locale = getLocale()
	return to_full(locale)
}

function capitalize(s){
	return s[0].toUpperCase()+s.slice(1)
}

function htmlDecode(input){
	var e = document.createElement('div');
	e.innerHTML = input;
	return e.childNodes[0].nodeValue;
  }

function removePunctuation(string) {
	string = string.replace(/[!-#%-\x2A,-/:;\x3F@\x5B-\x5D_\x7B}\u00A1\u00A7\u00AB\u00B6\u00B7\u00BB\u00BF\u037E\u0387\u055A-\u055F\u0589\u058A\u05BE\u05C0\u05C3\u05C6\u05F3\u05F4\u0609\u060A\u060C\u060D\u061B\u061E\u061F\u066A-\u066D\u06D4\u0700-\u070D\u07F7-\u07F9\u0830-\u083E\u085E\u0964\u0965\u0970\u0AF0\u0DF4\u0E4F\u0E5A\u0E5B\u0F04-\u0F12\u0F14\u0F3A-\u0F3D\u0F85\u0FD0-\u0FD4\u0FD9\u0FDA\u104A-\u104F\u10FB\u1360-\u1368\u1400\u166D\u166E\u169B\u169C\u16EB-\u16ED\u1735\u1736\u17D4-\u17D6\u17D8-\u17DA\u1800-\u180A\u1944\u1945\u1A1E\u1A1F\u1AA0-\u1AA6\u1AA8-\u1AAD\u1B5A-\u1B60\u1BFC-\u1BFF\u1C3B-\u1C3F\u1C7E\u1C7F\u1CC0-\u1CC7\u1CD3\u2010-\u2027\u2030-\u2043\u2045-\u2051\u2053-\u205E\u207D\u207E\u208D\u208E\u2329\u232A\u2768-\u2775\u27C5\u27C6\u27E6-\u27EF\u2983-\u2998\u29D8-\u29DB\u29FC\u29FD\u2CF9-\u2CFC\u2CFE\u2CFF\u2D70\u2E00-\u2E2E\u2E30-\u2E3B\u3001-\u3003\u3008-\u3011\u3014-\u301F\u3030\u303D\u30A0\u30FB\uA4FE\uA4FF\uA60D-\uA60F\uA673\uA67E\uA6F2-\uA6F7\uA874-\uA877\uA8CE\uA8CF\uA8F8-\uA8FA\uA92E\uA92F\uA95F\uA9C1-\uA9CD\uA9DE\uA9DF\uAA5C-\uAA5F\uAADE\uAADF\uAAF0\uAAF1\uABEB\uFD3E\uFD3F\uFE10-\uFE19\uFE30-\uFE52\uFE54-\uFE61\uFE63\uFE68\uFE6A\uFE6B\uFF01-\uFF03\uFF05-\uFF0A\uFF0C-\uFF0F\uFF1A\uFF1B\uFF1F\uFF20\uFF3B-\uFF3D\uFF3F\uFF5B\uFF5D\uFF5F-\uFF65]+/gi, '')
	return string.replace(/\s+/g, ' ').trim()
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
	// Mediawiki doesn't allow files to have spaces in their names, so it converts spaces to underscores when saving them
	imgName = imgName.replace(' ', '_')
	var hash = md5(imgName)
	var firsthex = hash.substring(0,1)
	var first2 = hash.substring(0,2)
	return '/images/'+firsthex+'/'+first2+'/'+imgName
}
  
var unhashThumbImage = function(imgName, width) {
	if(typeof width==='string' && width.endsWith('px')) {
		width = width.substring(0,width.length-2)
	}
	if(imgName.startsWith('File:')) {
		imgName = imgName.substring(5)
	}
	return 'https://archonarcana.com/thumb.php?f='+imgName+'&width='+width
}

var loadImage = function(image) {
	image.setAttribute('src', image.getAttribute('data-src'))
	image.onload = () => {
	  image.removeAttribute('data-src')
	}
  }

function getCardImage(card, opts) {
	var widtharg = opts.outputWidth? ` width="${opts.outputWidth}" ` : ''
	var heightarg = opts.outputHeight? ` height="${opts.outputHeight}" ` : ''
	var sizearg = widtharg + heightarg
	var image_file = card.image_number.replace('.png', '')
	if(opts && opts.splitGigantic && card.subtype && card.subtype.match(/gigantic/i)) {
		image_file = card.front_image
		return `<img src="${image_file}" alt="${card.card_title}" ${sizearg}/>`
	}
	if(multiHouseCards.indexOf(card.card_title)>=0 && card.house) {
		image_file = `${image_file}-${capitalize(card.house)}`
	}
	image_file = image_file + '.png'
	var full_image_file = unhashImage(image_file)
	var data_src = (opts && !opts.noFullUpdate) ? `data-src="${full_image_file}"` : ''
	if(opts && opts.width) {
		image_file = unhashThumbImage(image_file, opts['width'])
		return `<img src="${image_file}" alt="${card.card_title}" ${data_src} ${sizearg}/>`
	} else {
		return `<img src="${full_image_file}" alt="${card.card_title}" ${sizearg}/>`
	}
}

function updateCardImages() {
    var imgs = $('img[data-src]')
    imgs.map(function(i) {
      var self = imgs[i]
      self.onload = () => {
        loadImage(self)
      }
    })
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

function fileIsImage(source) {
	return source.startsWith("File:") && (
		source.endsWith('.png') || source.endsWith('.jpg') || source.endsWith('.webp')
	)
}

function renderWikitextToHtml(text) {
	var s = htmlDecode(text)
	// Internal Links
	s = s.replace(/\[\[.*?\]\]/g, function (link) {
		var linktext = link.slice(2, link.length-2)
		var linkparts = linktext.split('|')
		var linksource = linkparts[0]
		var linkname = linksource
		if(linkparts[1]) {
			linkname = linkparts[1]
		}
		if(fileIsImage(linksource)){
			return '<img src="'+unhashThumbImage(linksource,linkname)+'">'
		} else {
			return '<a href="/'+linksource+'">'+linkname+'</a>'
		}
	})
	// External Links
	s = s.replace(/\[.*?\]/g, function (link) {
		var linktext = link.slice(1, link.length-1).trim()
		var linkparts = linktext.split('|')
		var linksource = linktext
		var linkname = linktext
		if(linkparts[1]) {
			linksource = linkparts[0]
			linkname = linkparts[1]
		} else {
			linkparts = linktext.split(' ')
			if(linkparts[1]) {
				linksource = linkparts[0]
				linkname = linkparts.slice(1).join(' ')
			}
		}
		return '<a href="'+linksource+'">'+linkname+'</a>'
	})
	// Bold
	s = s.replace(/\'\'\'[^'].*?[^']\'\'\'/g, function (text) {
		return '<b>'+text.substring(3,text.length-3)+'</b>'
	})
	// Italics
	s = s.replace(/\'\'[^'].*?[^']\'\'/g, function (text) {
		return '<i>'+text.substring(2,text.length-2)+'</i>'
	})
	// Numbered list tags
	var lines = s.split('\n')
	var ol = false
	var ul = false
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
		} else if(!ul && line.startsWith('*')) {
			ul = true
			lines[i] = '<ul><li>' + line.substring(1) + '</li>'
		} else if (ul && line.startsWith('*')) {
			lines[i] = '<li>'+line.substring(1)+'</li>'
		} else if (ul && !line.startsWith('*')) {
			ul = false
			lines[i] = '</ul>'
		} else if (i<lines.length-1) {
			lines[i] = line + '\n'
		}
	}
	if(ol) {
		lines.push('</ol>')
	}
	if(ul) {
		lines.push('</ul>')
	}
	s = lines.join('')
	// Replace newlines
	s = s.replace(/\n+/g,'<br>')
	return s
}

function collapsible_block(heading_level, heading, inner_text, index) {
	return `<${heading_level}>${heading}</${heading_level}>
	${inner_text}`
	return `
<${heading_level} class="section-heading collapsible-heading open-block"
 'tabindex="0" aria-haspopup="true"
  aria-controls="content-collapsible-block-${index}">
<div class="mw-ui-icon mw-ui-icon-mf-expand mw-ui-icon-element mw-ui-icon-small
 mf-mw-ui-icon-rotate-flip indicator mw-ui-icon-flush-left"></div>
 <span class="mw-headline" id="${heading}">${heading}</span></${heading_level}>
 <div class="mf-section-1 collapsible-block open-block"
  id="content-collapsible-block-${index}"
  aria-pressed="true" aria-expanded="true">${inner_text}</div>`
}

var joined = function (pre, ar, post, logic, filter=function(x){return x}) {
	if (ar.length > 0) {
	  var nar = ar.filter(function (item) {
		return item
	  })
	  nar = nar.map(function (item) {
		return pre + filter(item.replace(/\_/g, '%20')) + post
	  })
	  if (nar.length > 0) {
		return '(' + nar.join('%20' + logic + '%20') + ')'
	  }
	}
	return ''
  }

var carousels = {};

function carousel(first_time) {
  var i
  var x = document.getElementsByClassName("carousel")
  if(first_time) {
	for (i = 0; i < x.length; i++) {
		var el = x[i]
		var id = el.getAttribute("data-carousel-id")
		if(!carousels[id]) {
			carousels[id] = []
		}
		carousels[id].push(el)
	}
  }
  for(var id in carousels) {
		var elements = carousels[id]
		for(var element of elements) {
			element.style.display = "none"
		}
		if(!first_time) {
			var firstElement = elements[0]
			elements.splice(0, 1)
			elements.push(firstElement)
		}
		elements[0].style.display = "block"
		setTimeout(carousel, elements[0].getAttribute("data-carousel-speed")) 
  }
}

function ajax(url, d) {
	if(!(url.search("https://")==0 || url.search("http://")==0)) {
		url = "https://"+window.location.host+url
	}
	return $.ajax(url, d)
}

export {parseQueryString, pageTitle, unhashImage, unhashThumbImage, renderWikitextToHtml,
	isElementInViewport, htmlDecode, uniques, collapsible_block, carousel, 
	joined, removePunctuation, getCardImage, updateCardImages, 
	getLocale, locales, getFullLocale, to_full, getLocaleFromSubdomain, ajax}
