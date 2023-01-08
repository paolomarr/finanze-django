var _myDateFormat = function(date){
	year = date.getFullYear();
	month = String(date.getMonth() + 1).padStart(2, '0');
	day = String(date.getDate()).padStart(2, '0');
	return `${year}-${month}-${day}`
}

var fetchSummaryAjax = function(dateFrom, dateTo) {
	// string dates
	dfString = _myDateFormat(dateFrom);
	dtString = _myDateFormat(dateTo);
	var XHR = new XMLHttpRequest();
	XHR.addEventListener('load', function () {
		// renderSummaryTable(JSON.parse(XHR.responseText));
		document.getElementById('tableBody').innerHTML = XHR.responseText;
	});
	XHR.addEventListener('error', function() {
		console.log(XHR.statusText);
	});
	var url = "/movimenti/summary/fetch";
	var params = { dateFrom: dfString, dateTo: dtString };
	var search = new URLSearchParams(params);
	XHR.open('GET', url + "?" + search.toString());
	XHR.send();
}
var buildURLFromMonthYearSelects = function() {
	var monthindex = document.getElementById('select-month').value - 1; // they come 1-based
	var year = document.getElementById('select-year').value;
	var dateFrom = new Date(year, monthindex, 1);
	var dateTo = new Date(year, monthindex + 1, 1);
	fetchSummaryAjax(dateFrom, dateTo);
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
		buildURLFromMonthYearSelects();
	});
	document.getElementById('select-year').addEventListener("change", () => {
		buildURLFromMonthYearSelects();
	});
	this.document.getElementById("dateFrom").addEventListener("change", () => {
		fetchSummaryFromDateRangeFields();
	});
	this.document.getElementById("dateTo").addEventListener("change", () => {
		fetchSummaryFromDateRangeFields();
	});

	buildURLFromMonthYearSelects();
});