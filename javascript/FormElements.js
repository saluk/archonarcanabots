import $ from 'jquery'
import 'select2'
import {parseQueryString} from './myutils'

var check_images = {
	'Brobnar': 'https://archonarcana.com/images/e/e0/Brobnar.png',
	'Dis': 'https://archonarcana.com/images/e/e8/Dis.png',
	'Logos': 'https://archonarcana.com/images/c/ce/Logos.png',
	'Mars': 'https://archonarcana.com/images/d/de/Mars.png',
	'Sanctum': 'https://archonarcana.com/images/c/c7/Sanctum.png',
	'Saurian': 'https://archonarcana.com/images/9/9e/Saurian_P.png',
	'Star_Alliance': 'https://archonarcana.com/images/7/7d/Star_Alliance.png',
	'Shadows': 'https://archonarcana.com/images/e/ee/Shadows.png',
	'Untamed': 'https://archonarcana.com/images/b/bd/Untamed.png',
	'Ekwidon': 'https://archonarcana.com/images/3/31/Ekwidon.png',
  	'Anomaly': 'https://archonarcana.com/images/8/88/Anomoly-tc.png',
  	'Unfathomable': 'https://archonarcana.com/images/1/10/Unfathomable.png'
}

var like_query = function(s){
	return s.replace('"', '%').replace("'", '%')
}

class EditField {
	constructor(type, field, props) {
	  this.type = type
	  this.field = field
	  this.label = ''
	  this.split_on = ''
	  this.values = []
	  this.presetValue = ''
	  this.checknumbers = false
	  this.divclass = ''
	  this.attach = ''
	  this.combo = false
	  this.basic = false
	  this.triggerAdvanced = false
	  this.hidden = false
	  this.defaultlabel = ''
	  this.placeholder = ''
	  Object.assign(this, props)
	  return this
	}
	getElement() {
	  return this.getElements()[0]
	}
	getElements() {
	  if(this.type === 'int') {
		return [$('[name='+this.field+'_min')[0], $('[name='+this.field+'_max')[0]]
	  }
	  return $('[name='+this.field+']')
	}
	addElement() {
	  var self=this
	  var form=self.attach
	  if(!this.presetValue) {
		this.presetValue = parseQueryString(this.field)
	  }
	  if(this.presetValue && !this.basic){
		this.triggerAdvanced = true
	  }
	  if(form === '') {
		return
	  }
	  // $(form).empty() breaks min/max fields
	  if (this.type === 'br') {
		$(form).append('<br>')
	  }
	  else if (this.type === 'text') {
		if(this.label && !this.hidden){
		  $(form).append('<label for="' + this.field + '">' + this.label + '</label>')
		}
		var h = ""
		if(this.hidden){
		  h = ' type="hidden" '
		}
		$(form).append(`
		<input name="${this.field}" ${h} value="${self.presetValue}" placeholder="${self.placeholder}"/>
`)
	  }
	  else if (this.type === 'select') {
		var defaultlabel = ''
		if(this.defaultlabel != '') {
			defaultlabel = 'label="'+this.defaultlabel+'"'
		}
		var options = []
		if(this.label) {
		  options.push('<label for="' + this.field + '">' + this.label + '</label>')
		}
		if(this.combo) {
		  options.push('<select class="js-multiple" name="'+this.field+'" multiple>')
		} else {
		  options.push('<select name="'+this.field+'">')
		}
		if(!this.combo){
		  options.push('<option '+defaultlabel+' value=""></option>')
		}
		this.values.map(function(option) {
		  var is_checked = ''
		  if (self.presetValue.match(option)) {
			is_checked = ' selected="true"'
		  }
		  options.push('<option label="'+option.replace(/_/g,' ')+'" value="'+option+'"'+is_checked+'>'+option+'</option>')
		})
		options.push('</select>')
		$(form).append(options.join(''))
  
		if(this.combo) {
		  var el = $('select[name="'+this.field+'"]')
		  el.select2()
		  // Sort by last item added
		  el.on("select2:select", function (evt) {
			var element = evt.params.data.element
			var $element = $(element)
			
			$element.detach()
			$(this).append($element)
			$(this).trigger("change")
		  })
		  this.presetValue.split('+').map(function(option) {
			var optionEl = $(el).find('[value="Name"]')
			optionEl.detach()
			$(el).append(optionEl)
		  })
		  $(el).trigger("change")
		}
  
	  }
	  else if (this.type === 'checkbox') {
		//$(form).append('<span>' + this.label + ': </span>')
		this.values.map(function(value) {
		  var img = check_images[value]
		  var txt = ''
		  txt += '<div class="'+self.divclass+'">'
		  // Input
		  txt += '<input type="checkbox" '
		  if(img){
			txt += 'class="checkbox-house"'
		  }
		  if(self.presetValue.replace(/\+/g,' ').match(value)) {
			txt += ' checked="true" '
		  }
		  txt += 'name="'+self.field+'" id="'+value+'" value="'+value+'">' 
		  // Label
		  txt += '<label class="checkbox-label" for="'+value+'"><span class="checkbox-custom">'
		  if(img){
			txt += '<span class="checkbox-checkbox"></span>'
			txt += '<img src="'+img+'" class="houseIcon">'
		  } else {
			txt += value.replace(/\_/g, ' ')
		  }
		  txt += '</span></label></div>'
		  $(form).append(txt)
		})
	  }
	}
	getData() {
	  if(this.type === 'text') {
		var val = this.getElement().value
		val = like_query(val)
		if(this.split_on.length>0) {
		  return val.split(this.split_on).map(function(to_trim) {
			  return to_trim.trim()
		  })
		}
		return [val.trim()]
	  } else if(this.type === 'select') {
		var vals = []
		if(!this.getElement().selectedOptions) {
		  return vals
		}
		var opts = this.getElement().selectedOptions
		for(var i=0; i<opts.length; i++) {
			if(opts[i].value.length>0) {
		  		vals.push(opts[i].value)
			}
		}
		return vals
	  }
	  else if(this.type === 'int') {
		return {
		  min: this.getElements()[0].value,
		  max: this.getElements()[1].value
		}
	  }
	  else if(this.type === 'checkbox') {
		var li = []
		var el = this.getElements()
		var self=this
		el.map(function(i) {
		  if(el[i].checked) {
			var val = el[i].value
			if(self.checknumbers) {
			  if(val==='0') {
				li.push('')
				li.push(val)
			  }
			} else {
			  li.push(val)
			}
		  }
		})
		return li
	  }
	  return undefined
	}
	assignData(ob) {
	  if(!this.getElement()) {
		  return
	  }
	  var d = this.getData()
	  if(d!==undefined) {
		ob[this.field] = d
	  }
	}
	listener(callback, search) {
	  var event = function() {
		callback(search)
	  }
	  if(this.type === 'text'){
		this.getElement().addEventListener('input', event)
	  } else if(this.type === 'checkbox') {
		var el = this.getElements()
		el.map(function(i) {
		  el[i].addEventListener('change', event)
		})
	  } else if(this.type === 'int') {
		this.getElements()[0].addEventListener('input', event)
		this.getElements()[1].addEventListener('input', event)
	  } else if(this.type === 'select') {
		if(this.combo){
		  return $('select[name="'+this.field+'"]').select2().on('change', event)
		}
		this.getElement().addEventListener('change', event)
	  }
	}
  }
  
  var minmax = function(array, field, attach, values, hidemax=false, min_label="Min ") {
	array.push(new EditField('select', field+'_min', {'label':min_label,'attach':attach, 'values':values}))
	if(!hidemax) {
	  array.push(new EditField('select', field+'_max', {'label':'Max ','attach':attach, 'values':values}))
	}
  }

  export {EditField, minmax}