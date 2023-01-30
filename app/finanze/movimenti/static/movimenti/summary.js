var _myDateFormat = function(date){
	year = date.getFullYear();
	month = String(date.getMonth() + 1).padStart(2, '0');
	day = String(date.getDate()).padStart(2, '0');
	return `${year}-${month}-${day}`
};

var _fillChart = function(chartId, data) {
	var chart = Chart.getChart(chartId);
	if (chart !== undefined) { // defined already
		chart.destroy();
	}
	var ctx = document.getElementById(chartId);
	new Chart(ctx, {
		type: 'pie',
		cutout: 0,
		data: data,
		options: {}
	});
}
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
		_fillChart('expensesChart', { labels: outlabels, datasets: [{data: outvalues, label: "Expenses"}] });
		_fillChart('incomesChart', { labels: inlabels, datasets: [{data: invalues, label: "Incomes"}] });
	};
	_fetch(dateFrom, dateTo, "json", success);
};
var fetchSummaryAjax = function (dateFrom, dateTo) {
	var success = function(xhr) {
		document.getElementById('summaryTableContainer').innerHTML = xhr.responseText;
	};
	_fetch(dateFrom, dateTo, "fetch", success);
}
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
var fetchSummaryFromDateRangeFields = function () {
	from = document.getElementById('dateFrom').value;
	to = document.getElementById('dateTo').value;
	if (from !== undefined && from.length > 0 &&
		to !== undefined && to.length > 0) {
		fetchSummaryAjax(new Date(from), new Date(to));
	}
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
		fetchSummaryFromDateRangeFields();
		fetchChartData(range[0], range[1]);
	});
	document.getElementById("dateTo").addEventListener("change", () => {
		fetchSummaryFromDateRangeFields();
		fetchChartData(range[0], range[1]);
	});

	var range = buildDateRangeFromSelects();
	fetchSummaryAjax(range[0], range[1]);
	fetchChartData(range[0], range[1]);
});