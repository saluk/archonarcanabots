/* Any JavaScript here will be loaded for all users on every page load. */
var houses = ['Brobnar','Dis','Logos','Mars','Sanctum','Saurian','Star Alliance','Shadows','Untamed'];
var sets = ['Call of the Archons', 'Age of Ascension', 'Worlds Collide', 'Mass Mutation'];
var types = ['Creature', 'Artifact', 'Upgrade', 'Action'];
var house_arg = 'DPL_arg1';
var set_arg = 'DPL_arg2';
var type_arg = 'DPL_arg3';

var parseQueryString = function(argument) {
  console.log(window.location.href);
  var res = '[\\?&]'+argument+'=([^&#]*)';
  console.log(res);
  var found = new RegExp(res).exec(window.location.href);
  if(found){
	return decodeURIComponent(found[1]);
  } else {
  	return '';
  }
};

var house_images = {
	'Brobnar': 'https://archonarcana.com/images/e/e0/Brobnar.png',
	'Dis': 'https://archonarcana.com/images/e/e8/Dis.png',
	'Logos': 'https://archonarcana.com/images/c/ce/Logos.png',
	'Mars': 'https://archonarcana.com/images/d/de/Mars.png',
	'Sanctum': 'https://archonarcana.com/images/c/c7/Sanctum.png',
	'Saurian': 'https://archonarcana.com/images/9/9e/Saurian_P.png',
	'Star Alliance': 'https://archonarcana.com/images/7/7d/Star_Alliance.png',
	'Shadows': 'https://archonarcana.com/images/e/ee/Shadows.png',
	'Untamed': 'https://archonarcana.com/images/b/bd/Untamed.png'
};

var buildCategoryList = function(line_length, parent, categoryArray, searches, labelText, images) {
	parent.appendChild(document.createTextNode(labelText + " "));
	categoryArray.forEach(function(category) {
		var input = document.createElement('input');
		input.setAttribute('type','checkbox');
		var searchmatch = '(^|[\|])' + category.replace(/\+/g,' ') + '([\|]|$)';
        console.log(searchmatch, searches);
		if(searches.replace(/\+/g,' ').match(searchmatch)) {
			input.setAttribute('checked','true');
		}
		input.setAttribute('name','category');
		input.setAttribute('id','category_'+category);
		input.setAttribute('value',category);
		
		var label = document.createElement('label');
		label.setAttribute('for','category_'+category);
		
		var span = document.createElement('span');
		
		if(images){
			input.setAttribute('class','checkbox-house');
			label.setAttribute('class','checkbox-label');
			span.setAttribute('class','checkbox-custom');
			var span2 = span.appendChild(document.createElement('span'));
			span2.setAttribute('class','checkbox-checkbox');
			var img = span.appendChild(document.createElement('img'));
			img.setAttribute('src',house_images[category]);
		} else {
			span.appendChild(document.createTextNode(category));
		}
		
		parent.appendChild(input);
		parent.appendChild(label);
		label.appendChild(span);
		line_length -= 1;
		if(line_length<=0){
			line_length = 4;
			parent.appendChild(document.createElement('br'));
		}
	});
	parent.appendChild(document.createElement('br'));
};

var findSearches = function(categories) {
	var s = "";
	categories.forEach(function(category) {
		if(document.getElementById('category_'+category).checked===true) {
			s += category + '|';
		}
	});
	return s.substr(0,s.length-1);
};

var doSearch = function() {
	console.log('doing the search');
	var dpl = function(name, search) {
		document.getElementById(name).setAttribute('value',search);
	};
	dpl(house_arg,findSearches(houses));
	dpl(set_arg,findSearches(sets));
	dpl(type_arg,findSearches(types));
	document.getElementById('searchForm').submit();
};

var buildSubmitButton = function(parent) {
	var dpl = function(name) {
		var hidden = document.createElement('input');
		hidden.setAttribute('type','hidden');
		hidden.setAttribute('name',name);
		hidden.setAttribute('id',name);
		hidden.setAttribute('value','');
		parent.appendChild(hidden);
	};
	[house_arg, type_arg, set_arg].forEach(dpl);
	var hidden2 = document.createElement('input');
	hidden2.setAttribute('type','hidden');
	hidden2.setAttribute('name','title');
	hidden2.setAttribute('value',parseQueryString('title'));
	parent.appendChild(hidden2);
	var submit = document.createElement('button');
	submit.setAttribute('type','button');
	submit.appendChild(document.createTextNode('search'));
	//submit.setAttribute('onClick','doSearch()');
	submit.addEventListener ("click", doSearch, false);
	parent.appendChild(submit);
	parent.appendChild(document.createElement('br'));
};

var buildViewCardsForm = function(line_length) {
	var searches = {};
	[house_arg,type_arg,set_arg].forEach(function(name) {
		searches[name] = parseQueryString(name).replace("+"," ");
    });
	console.log(searches);
	var form = document.createElement('form');
	form.setAttribute('method', 'GET');
	form.setAttribute('id','searchForm');
	buildCategoryList(line_length, form, houses, searches[house_arg], "Houses:", true);
	buildCategoryList(line_length, form, sets, searches[set_arg], "Sets:", false);
    buildCategoryList(line_length, form, types, searches[type_arg], "Types:", false);
    $(form).append('<label for="cardname">Card Name: </label>');
    $(form).append('<input name="cardname" value="'+parseQueryString('cardname')+'" />');
	buildSubmitButton(form);
	document.getElementById('viewcards_form').appendChild(form);
};


var buildPages = function() {
	var footer = document.getElementById('pages');
	var max = Number(footer.textContent.split("/")[1]);
	footer.innerHtml = '';
	
	var offset = Number(parseQueryString('DPL_offset') || 0);
	var prev = document.createElement('a');
	prev.setAttribute('href',
				   '/Card_Gallery?DPL_arg1='+parseQueryString('DPL_arg1')+
				   '&DPL_arg3='+parseQueryString('DPL_arg3')+
				   '&DPL_arg2='+parseQueryString('DPL_arg2')+
				   '&DPL_offset='+(offset-50));
	prev.appendChild(document.createTextNode(' < prev '));
	var next = document.createElement('a');
	next.setAttribute('href',
				   '/Card_Gallery?DPL_arg1='+parseQueryString('DPL_arg1')+
				   '&DPL_arg3='+parseQueryString('DPL_arg3')+
				   '&DPL_arg2='+parseQueryString('DPL_arg2')+
				   '&DPL_offset='+(offset+50));
	next.appendChild(document.createTextNode(' next >'));
	if(offset-50>=0) {
		document.getElementById('resultsheader').appendChild(prev);
		footer.appendChild(prev.cloneNode(true));
	}
	position = document.createTextNode(' ' + Number.parseInt(offset/50+1) + ' / ' + Number.parseInt(max/50+1) + ' ');
	document.getElementById('resultsheader').appendChild(position);
	footer.appendChild(position.cloneNode(true));
	if(offset+50<max) {
		document.getElementById('resultsheader').appendChild(next);
		footer.appendChild(next.cloneNode(true));
	}
};

var init_dpl_search = function(line_length) {
	if(document.getElementById('viewcards_form')) {
		buildViewCardsForm(line_length);
	}
	if(document.getElementById('pages')) {
		buildPages();
	}
}
