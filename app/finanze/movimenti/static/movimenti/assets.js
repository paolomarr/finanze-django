// NOT WORKING here
// import date-fns locale:
// import { it } from 'date-fns/locale';
var chartdata = {};
var _renderChart = function (chartId) {
	var chart = Chart.getChart(chartId);
	if (chart !== undefined) { // defined already
		chart.destroy();
	}
	var ctx = document.getElementById(chartId);
	var datasets = []
	for(const series of [
		"timeseries", 
		"assets",
	]){
		if (chartdata[series].chartdata.data.length > 0) {
			datasets.push({
				label: chartdata[series].chartdata.title,
				data: chartdata[series].chartdata.data
			})
		}
	}
	var chartConfig = {
		type: 'line',
		data: {datasets: datasets},
		options: {
			plugins: {
				title: {
					text: chartdata.timeseries.chartdata.title,
					display: true
				},
				legend: { display: true}
			},
			parsing: {
				'xAxisKey': 'date',
				'yAxisKey': 'totbalance'
			},
			scales: {
				x: {
					type: 'time',
					time: {
						// Luxon format string
						tooltipFormat: 'MMM yyyy'
					},
					title: {
						display: true,
						text: chartdata.timeseries.chartdata.xTitle
					},
					// adapters: {
					// 	date: {
					// 		locale: it
					// 	}
					// }
				},
				y: {
					title: {
						display: true,
						text: chartdata.timeseries.chartdata.yTitle
					}
				}
			},
			aspectRatio: 1,
		},
	};
	new Chart(ctx, chartConfig);
};
var insertNewListItem = function() {
	// return inputrow;
	var itemsList = document.getElementById('itemsList');
	var currentItems = itemsList.childElementCount - 1; // -1 to exclude the hidden template
	var newitem = document.getElementById('balanceListItemTemplate').cloneNode(true);
	newitem.id = `balance_item_${currentItems}`;
	newitem.setAttribute('data-index', currentItems);
	newitem.querySelector('[name=balance_item_key]').id = `balance_item_key_${currentItems}`;
	newitem.querySelector('[name=balance_item_val]').id = `balance_item_val_${currentItems}`;
	newitem.classList.remove("d-none");
	itemsList.append(newitem);
};
var removeButtonClick = function(element){
	index = parseInt(element.getAttribute('data-index'));
	idtoremove = `balance_item_${index}`;
	document.getElementById(idtoremove).remove();

	computeSum();
};
var computeSum = function(){
	var sum = 0;
	var numinputs = document.getElementsByName('balance_item_val');
	numinputs.forEach(element => {
		val = parseFloat(element.value)	
		if(! isNaN(val)) sum += val;
	});
	document.getElementById('sum').innerHTML = sum.toFixed(2);
	document.getElementById('id_balance').value = sum;
};
var getAssetItemsObjects = function(){
	var objects = [];
	var allrows = document.getElementById('itemsList').querySelectorAll('div.row');
	for(var i = 0; i<allrows.lengthl; i++){
		currow = allrows[i];
		keyinput = currow.getElementsByTag('input')[0];
		valueinput = currow.getElementsByTag('input')[1];
		if(keyinput.value == "")  return;
		key = keyinput.value;
		val = valueinput.value;
		var object = {
			"key": key, "val": val
		};
		objects.push(object);
	}
	console.log(objects);
}
var keyItemChange = function(element){
	getAssetItemsObjects();
}
var fetchChartData = function() {
	const timeseriesXHR = new XMLHttpRequest();
	timeseriesXHR.addEventListener('load', function () {
		jdata = JSON.parse(timeseriesXHR.responseText);
		chartdata['timeseries'] = jdata;
		if('assets' in chartdata)
			_renderChart("assetsChart");
	});
	timeseriesXHR.addEventListener('error', (event) => {});
	timeseriesXHR.open('GET', "/movimenti/timeseries");
	timeseriesXHR.send();

	const assetsXHR = new XMLHttpRequest();
	assetsXHR.addEventListener('load', function () {
		jdata = JSON.parse(assetsXHR.responseText);
		chartdata['assets'] = jdata;
		if ('timeseries' in chartdata)
			_renderChart("assetsChart");
	});
	assetsXHR.addEventListener('error', (event) => { });
	assetsXHR.open('GET', "/movimenti/assets/json");
	assetsXHR.send();
}
var itemscounter = 0;
window.addEventListener("load", function(event) {
	// Callbacks
	var addbutton = document.getElementById('addbutton');
	addbutton.addEventListener("click", function(){
		insertNewListItem();
	});
	addbutton.click();

	var now = new Date().toISOString();
	now = now.replace(/\.\d+Z?$/, '');
	var dateInput = document.getElementsByName('date')[0];
	var submitInput = document.getElementsByName('submit')[0];
	dateInput.setAttribute('step', 1);
	dateInput.value = now;
	submitInput.addEventListener("click", function(){
		document.getElementById('messages').innerHTML = "";
		var assetsForm = document.getElementById('assetsForm');
		url = assetsForm.getAttribute('action');
		date = dateInput.value;
		csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
		var serialized = new URLSearchParams();
		serialized.append("csrfmiddlewaretoken", csrftoken);
		serialized.append("date", date);
		var balance_items = document.getElementsByName('balance_item_val');
		var balance_items_keys = document.getElementsByName('balance_item_key');
		for(let i = 0; i<balance_items.length; i++){
			key = balance_items_keys[i].value;
			el = balance_items[i];	
			val = el.value;
			if(val.length == 0) 	continue;
			serialized.append("balance_item_val", val);
			serialized.append("balance_item_key", key);
		}
		const XHR = new XMLHttpRequest();
		// Define what happens on successful data submission
		XHR.addEventListener('load', function () {
			var response = JSON.parse(XHR.responseText);
			// warnings first
			if (response.warnings.length > 0) {
				response.warnings.forEach(element => {
					var warningline = document.createElement('p');
					warningline.classList.add('alert-warning')
					document.getElementById('messages').append(warningline);
				});
			}
			if(response.errors.length > 0){
				response.errors.forEach(element => {
					var errorline = document.createElement('p');
					errorline.classList.add('alert-danger')
					document.getElementById('messages').append(errorline);
				});
			}else{
				window.location.reload();
			}
		});

		// Define what happens in case of an error
		XHR.addEventListener('error', (event) => {
			alert('Oops! Something went wrong.');
			// err = data.errors;
			// if (err.length > 0) {
			// 	err.each((idx, el) => {
			// 		$('#messages').append(`<p class="bg-warning">${err}</p>`);
			// 	})
			// } else {
			// 	$('#messages').append(`<p class="bg-primary text-white">${err}</p>`);
			// }
		});
		// Set up our request
		XHR.open('POST', url);
		XHR.send(serialized);
	});
	fetchChartData();
});