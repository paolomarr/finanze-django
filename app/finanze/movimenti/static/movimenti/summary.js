var _renderChart = function(chartId, data) {
	var chart = Chart.getChart(chartId);
	if (chart !== undefined) { // defined already
		chart.destroy();
	}
	/**
	 * 
	 */
	var ctx = document.getElementById(chartId);
	var myPieChart = new Chart(ctx, {
		type: 'pie',
		cutout: 0,
		data: data,
		options: {
			plugins: {
				tooltip: {
					callbacks: {
						label: function (context) {
							var total = context.dataset.data.reduce(function (previousValue, currentValue, currentIndex, array) {
								return previousValue + currentValue;
							});
							var currentValue = context.parsed.toFixed(2);
							var percentage = Math.floor(((currentValue / total) * 100) + 0.5).toFixed(1);
							return `${currentValue} (${percentage}%)`;
						}
					}
				},
			},
			// legendCallback: function (chart) {
			// 	var text = [];
			// 	text.push('<ul class="' + chart.id + '-legend">');
			// 	for (var i = 0; i < chart.data.datasets[0].data.length; i++) {
			// 		text.push('<li><span style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>');
			// 		if (chart.data.labels[i]) {
			// 			text.push(chart.data.labels[i] + " - " + Math.floor((chart.data.datasets[0].data[i] / chart.data.datasets[0]._meta[0].total) * 100 + 0.5) + "%");
			// 		}
			// 		text.push('</li>');
			// 	}
			// 	text.push('</ul>');
			// 	return text.join("");
			// }
		}
	});
};
var fetchChartData = function (dateFrom, dateTo) {
	var success = function (xhr) {
		var data = JSON.parse(xhr.responseText);
		var outlabels = [];
		var inlabels = [];
		var outvalues = [];
		var invalues = [];
		for(var i=0; i<data.results.length; i++){
			item = data.results[i];
			if(item.empty) 	continue;
			var inval = parseFloat(item.ins.amount);
			var outval = parseFloat(item.outs.amount);
			if(inval > 0.0){
				inlabels.push(item.cat.cat);
				invalues.push(inval);
			}
			if (outval > 0.0){
				outlabels.push(item.cat.cat)
				outvalues.push(outval);
			}
		}
		_renderChart('expensesChart', { labels: outlabels, datasets: [{data: outvalues, label: "Expenses"}] });
		_renderChart('incomesChart', { labels: inlabels, datasets: [{data: invalues, label: "Incomes"}] });
	};
	_fetch(dateFrom, dateTo, "json", success);
};
var fetchSummaryAjax = function (dateFrom, dateTo) {
	var success = function(xhr) {
		document.getElementById('summaryTableContainer').innerHTML = xhr.responseText;
	};
	_fetch(dateFrom, dateTo, "fetch", success);
};
var _fetch = function(dateFrom, dateTo, mode, success) {
	// string dates
	dfString = _myDateFormat(dateFrom);
	dtString = _myDateFormat(dateTo);
	var XHR = new XMLHttpRequest();
	XHR.addEventListener('load', function () {
		success(XHR);
	});
	XHR.addEventListener('error', function() {
		console.log(XHR.statusText);
	});
	var url = `/movimenti/summary/${mode}`;
	var params = { dateFrom: dateFrom.toISOString(), dateTo: dateTo.toISOString() };
	var search = new URLSearchParams(params);
	XHR.open('GET', url + "?" + search.toString());
	XHR.send();
}
var buildDateRangeFromSelects = function() {
	var monthindex = document.getElementById('select-month').value - 1; // they come 1-based
	var year = document.getElementById('select-year').value;
	var dateFrom = new Date(year, monthindex, 1);
	var dateTo = new Date(year, monthindex + 1, 1);
	return [dateFrom, dateTo];
}
var buildDateRangeFromFromAndTo = function () {
	from = document.getElementById('dateFrom').value;
	to = document.getElementById('dateTo').value;
	if (from !== undefined && from.length > 0 &&
		to !== undefined && to.length > 0) {
		return [new Date(from), new Date(to)];
	}
	return null;
}
window.addEventListener("load", function(){
	document.getElementById('select-month').addEventListener("change", () => {
		var range = buildDateRangeFromSelects();
		fetchSummaryAjax(range[0], range[1]);
		fetchChartData(range[0], range[1]);
	});
	document.getElementById('select-year').addEventListener("change", () => {
		var range = buildDateRangeFromSelects();
		fetchSummaryAjax(range[0], range[1]);
		fetchChartData(range[0], range[1]);
	});
	document.getElementById("dateFrom").addEventListener("change", () => {
		var range = buildDateRangeFromFromAndTo();
		if(range){
			fetchChartData(range[0], range[1]);
		}
	});
	document.getElementById("dateTo").addEventListener("change", () => {
		var range = buildDateRangeFromFromAndTo();
		if(range){
			fetchSummaryAjax(range[0], range[1]);
			fetchChartData(range[0], range[1]);
		}
	});
	document.getElementById('filter-button-currentyear').addEventListener("click", () => {
		today = new Date();
		from = new Date(today.getFullYear(), 0, 1, 0, 0, 0);
		to = today;
		fetchSummaryAjax(from, to);
		fetchChartData(from, to);
	});
	document.getElementById('filter-button-lastyear').addEventListener("click", () => {
		today = new Date();
		from = new Date(today.getFullYear() -1, 0, 1, 0, 0, 0);
		to = new Date(today.getFullYear(), 0, 1, 0, 0, 0);
		fetchSummaryAjax(from, to);
		fetchChartData(from, to);
	});
	document.getElementById('filter-button-last3m').addEventListener("click", () => {
		to = new Date();
		from = new Date(Date.now() - 3 * 30 * 24 * 3600 * 1000); // flawed: assuming fixed 30 day-months
		fetchSummaryAjax(from, to);
		fetchChartData(from, to);
	});
	document.getElementById('filter-button-last6m').addEventListener("click", () => {
		to = new Date();
		from = new Date(Date.now() - 6 * 30 * 24 * 3600 * 1000); // flawed: assuming fixed 30 day-months
		fetchSummaryAjax(from, to);
		fetchChartData(from, to);
	});
	document.getElementById('filter-button-last12m').addEventListener("click", () => {
		to = new Date();
		from = new Date(to.getFullYear() - 1, to.getMonth(), to.getDate(), to.getHours(), to.getMinutes(), to.getSeconds());
		fetchSummaryAjax(from, to);
		fetchChartData(from, to);
	});
	var range = buildDateRangeFromSelects();
	fetchSummaryAjax(range[0], range[1]);
	fetchChartData(range[0], range[1]);
});