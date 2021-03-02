import {getLocale} from './myutils'

function show_translations() {
	$('.translate').css('display','none')
	$('.translate-'+getLocale()).css('display','inline')
}

function dumb_locale_menu() {
	var locales = {"pt-pt": [["pt-br", "Português do Brasil"], ["pt", "português"]],
	"it-it": [["it", "Italiano"]],
	"zh-hant": [["zh-hant", "中文（繁體）"], ["zh-tw", "中文（台灣）"]],
	"de-de": [["de", "Deutsch"], ["de-formal", "Deutsch (Sie-Form)"]],
	"zh-hans": [["zh", "中文"], ["zh-hans", "中文（简体）"]],
	"th-th": [["th", "ไทย"]],
	"ko-ko": [["ko", "한국어"], ["ko-kp", "조선말"]],
	"pl-pl": [["pl", "Polski"]],
	"fr-fr": [["fr", "Français"], ["frc", "français cadien"]],
	"es-es": [["es", "Español"]],
	'ru-ru': [['ru', "Pусский"]],
	"en": [["en", "English"]]}
	var locale = ''
	for(const [loc, value] of Object.entries(locales)) {
		if(loc=='en') {
			var path = ''
		} else {
			var path = '/locale/'+value[0][0]
		}
		var locale_name = value[0][1]
		var cardname = window.location.href.split('archonarcana.com/')[1].split('/')[0]
		var selected = ''
		var sp = window.location.href.split('/')
		if (value[0][0]==sp[sp.length-1]) selected='selected'
		locale += `<option value="/${cardname}${path}" ${selected}>${locale_name}</option>`
	}
	var base = `<div>
	View in <select name="viewlanguage" onchange="location = this.value;">
	${locale}
	</select> 
	</div>`
	if($('.cardEntry').length > 0 && window.location.href.search('/locale/')>=0) {
		$('.mw-parser-output').before(base)
	}
}

export {show_translations, dumb_locale_menu}