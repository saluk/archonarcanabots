import * as $ from 'jquery'
import {parseQueryString, pageTitle, to_full} from './myutils'
import {set_name_by_number} from './data'
import ApexCharts from 'apexcharts'

function chartCounts(counts) {
  var labels = []
  for(var i=1; i<=36; i++) {
    labels.push(i)
  }
  var globaldata = {
    labels: labels,
    datasets: []
  }
  var colors = [
    'rgb(203, 66, 245)',
    'rgb(197, 245, 66)',
    'rgb(126, 245, 66)',
    'rgb(66, 245, 173)',
    'rgb(66, 245, 224)',
    'rgb(66, 206, 245)'
  ]
  var has_copy_data = {}
  for(var expansion of Object.keys(counts)) {
    var copydata = []
    for(var copies=1; copies<=36; copies++) {
      var val = counts[expansion][copies.toString()]
      if(val) {
        copydata.push(val)
        has_copy_data[copies] = true
      } else {
        copydata.push(0)
      }
    }
    var color = colors.pop()
    globaldata.datasets.push({
      label: set_name_by_number(expansion),
      data: copydata,
      borderColor: '#000000',
      backgroundColor: color
    })
    colors.unshift(color)
  }
  console.log(has_copy_data)
  var off = 0
  for(var i=1; i<=36; i++) {
    if(has_copy_data[i] == undefined) {
      globaldata.labels.splice(i-1+off, 1)
      for(var expansion_count of globaldata.datasets) {
        expansion_count.data.splice(i-1+off, 1)
      }
      off -= 1
    } else {
      console.log('ok '+i)
    }
  }
  console.log(globaldata.labels)
  var config = {
    type: 'bar',
    data: globaldata,
    scales: {
      xAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: "# Copies"
          }
        }
      ]
    },
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
  config = {
    chart: {
      type: 'bar'
    },
    plotOptions: {
      bar: {
        horizontal: true
      }
    },
    series: [{
      name: 'worlds collide',
      data: [10000, 1000, 10, 1]
    }, {
      name: 'mass mutation',
      data: [1000, 100, 1, 0]
    }],
    xaxis: {
      categories: [1, 2, 3, 4]
    },
    legend: {
      show: true
    }
  }
  var chart = new ApexCharts(document.getElementById('counts_chart'), config);
  chart.render();
}

function getStats(cardname) {
    var el = $('#statsDisplay')
    $.ajax(`https://keyforge.tinycrease.com/card_stats?card_name=${cardname}`,
      {
        success: function (data, status, xhr) {
          el.empty()
          //text = `<div><canvas id="counts_chart" style="width:300px;height:300px"></canvas></div>`
          text = '<div id="counts_chart"></div>'
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
