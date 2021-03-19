import Chart from 'chart.js'

function replace_charts() {
	var divs = $('.genchart')
	divs.map(function(id){
		var div = divs[id]
		var data = JSON.parse($(div).text())
		$(div).empty()
		$(div).append('<canvas id="myChart"></canvas>')
		var ctx = $(div).children()[0].getContext('2d');
		var myChart = new Chart(ctx, data);
		$(div)[0].style.display=""
	})
}

export {replace_charts}