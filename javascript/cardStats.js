import {parseQueryString, pageTitle, to_full} from './myutils'
import {set_name_by_number} from './data'
import Chart from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
Chart.plugins.register(ChartDataLabels);

var colors = [
  '#dedcd3',
  '#eedcd3',
  '#fedcd3',
  '#9edcd3',
  '#8edcd3',
  '#7edcd3',
  '#6edcd3',
  '#5edcd3',
  '#4edcd3'
]

function chartCounts(counts) {
  var labels = Object.keys(counts).map(expansion=>set_name_by_number(Number(expansion)))
  var globaldata = {
    labels: labels,
    datasets: []
  }
  for(var copies=1;copies<=36;copies++) {
    var copydata = []
    for(var expansion_counts of Object.values(counts)) {
      copydata.push(expansion_counts[copies.toString()] || 0)
    }
    if(copydata.filter(x=>x>0).length==0) {
      continue
    }
    var color = colors.pop()
    globaldata.datasets.push({
      label: copies,
      data: copydata,
      borderColor: '#ffffff',
      backgroundColor: color
    })
    colors.unshift(color)
  }
  var config = {
    type: 'bar',
    data: globaldata,
    options: {
      indexAxis: 'y',
      elements: {
        bar: {
          borderWidth: 2
        }
      },
      responsive: false,
      plugins: {
        legend: {
          position: 'right'
        },
        title: {
          display: true,
          text: 'Copy counts in each set'
        }
      }
    }
  }
  console.log(config)
	var myChart = new Chart(document.getElementById('counts_chart'), config)
}

function getStats(cardname) {
    var el = $('#statsDisplay')
    $.ajax(`https://keyforge.tinycrease.com/card_stats?card_name=${cardname}`,
      {
        success: function (data, status, xhr) {
          el.empty()
          text = `<div><canvas id="counts_chart" style="width:300px;height:300px"></canvas></div>`
          el.append(text)
          chartCounts(data['counts'])
        },
        error: function(req, status, error) {
          el.append('<div>Error loading stats</div>')
        }
      }
    )
}

function renderCardStats() {
    var cardEntry = $('.cardEntry')
    var title = pageTitle()
    console.log(cardEntry)
    if(cardEntry && parseQueryString('testjs')==='true'){
      cardEntry.after('<h2><span class="mw-headline">Stats</span></h2><div id="statsDisplay">Loading...</div>')
      getStats(title)
    }
}

export {renderCardStats}