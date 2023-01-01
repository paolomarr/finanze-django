/*
{
	"results":[
		{"cat":"Affitto (in)","outs":{"amount":0},"ins":{"amount":0}},
		{"cat":"Altro","outs":{"amount":0},"ins":{"amount":0}},
		{"cat":"Altro (in)","outs":{"amount":0},"ins":{"amount":0}},
		{"cat":"Casa / Elettrodomestici","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Donazioni / Beneficienza","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Fabri (in)","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Internet / TV / Telefono / Musica","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Luce / Gas / Acqua / Spese cond","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Mutuo","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Online Shopping","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Palestra / Sport","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Ristoranti / Bar","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Sanità","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Spese Supermercato","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Stipendio","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Tasse","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Trasporti","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Vestiti","outs":{"amount":0},"ins":{"amount":0}},{"cat":"Viaggi","outs":{"amount":0},"ins":{"amount":0}}
	],
	"totals":{"ins":0,"outs":0},
	"start":"2022-12-02",
	"end":"2022-12-17"
}
*/

var _myDateFormat = function(date){
	year = date.getFullYear();
	month = String(date.getMonth() + 1).padStart(2, '0');
	day = String(date.getDate()).padStart(2, '0');
	return `${year}-${month}-${day}`
}

var tableheaderColumnFactory = function(header, smWidth, extraClasses = []) {
	clss = extraClasses.join(' ');
	return `<div class="table-header col-12 col-sm-${smWidth} ${clss}">${header}</div>`
}
var tableRowFieldFactory = function (field, iconclass, smWidth = 1, extraClasses = []) {
	clss = extraClasses.join(' ');
	return `<div class="col-12 col-sm-${smWidth} ${clss}">
		<span class="d-sm-none"><i class="bi bi-${iconclass}"></i></span>
		${field}
	</div>
	`
}
var tableRowFactory = function(rowobj, datefrom, dateto) {
	rows = "";
	catobj = rowobj['cat']
	filterqueryobj = new URLSearchParams({ filter: encodeURIComponent(`category=${catobj.id}`)});
	if(dateto !== undefined){
		filterqueryobj.append("filter", encodeURIComponent(`dateto=${dateto}`));
	}
	if(datefrom !== undefined){
		filterqueryobj.append("filter", encodeURIComponent(`datefrom=${datefrom}`));
	}
	filterstr = filterqueryobj.toString();
	catlinkuri = `/movimenti/list?${filterstr}`;
	catlink = `<a href="${catlinkuri}" data-category=${catobj.id}>${catobj.cat}</a>`
	rows += tableRowFieldFactory(catlink, "tag", 6, []);
	rows += tableRowFieldFactory(rowobj['ins']['amount'].toFixed(2),  "piggy-bank", 3, ["currency", "text-sm-end"]);
	rows += tableRowFieldFactory(rowobj['outs']['amount'].toFixed(2),  "wallet", 3, ["currency", "text-sm-end"]);
	return `<div class="row border-bottom">
		${rows}
	</div>`;
}
var tableTotalsRowFactory = function(totIn, totOut){
	rows = "";
	rows += tableRowFieldFactory("TOTALS", "", 6);
	rows += tableRowFieldFactory(totIn.toFixed(2), "", 3, ["currency", "text-sm-end"]);
	rows += tableRowFieldFactory(totOut.toFixed(2), "", 3, ["currency", "text-sm-end"]);
	return `<div class="d-none d-sm-flex row border-bottom table-total">
		${rows}
	</div>`;
}
var renderSummaryTable = function (tabledata) {
	start = (new Date(tabledata.start)).toLocaleDateString();
	end = (new Date(tabledata.end)).toLocaleDateString();
	$("#tableTitle").html(`You're viewing movements from ${start} to ${end}`);
	$("#tableHeader").empty();
	$("#tableBody").empty();
	$("#tableHeader").append(tableheaderColumnFactory("Category", 6));
	$("#tableHeader").append(tableheaderColumnFactory("Incomes", 3, ["text-sm-end"]));
	$("#tableHeader").append(tableheaderColumnFactory("Expenses", 3, ["text-sm-end"]));
	tabledata.results.forEach(element => {
		$("#tableBody").append(tableRowFactory(element, tabledata.start, tabledata.end));
	});
	$("#tableBody")
		.append(tableTotalsRowFactory(tabledata.totals.ins.amount, tabledata.totals.outs.amount));
}

var fetchSummaryAjax = function(dateFrom, dateTo) {
	// string dates
	dfString = _myDateFormat(dateFrom);
	dtString = _myDateFormat(dateTo);
	$.ajax("/movimenti/summary/json", {
		method: "GET",
		data: {dateFrom: dfString, dateTo: dtString},
		success: function(data) {
			renderSummaryTable(data)
		},
		error: function(xhr, status, errorstr) {
			console.log(`${status}: ${errorstr}`);	
		}
	});
}
var buildURLFromMonthYearSelects = function() {
	var monthindex = $('#select-month').val() - 1; // they come 1-based
	var year = $('#select-year').val();
	var dateFrom = new Date(year, monthindex, 1);
	var dateTo = new Date(year, monthindex + 1, 1);
	fetchSummaryAjax(dateFrom, dateTo);
}
$(function(){
	$('#select-month, #select-year').change(event => {
		buildURLFromMonthYearSelects();
	});
	$('#dateFrom, #dateTo').change(event => {
		from = $('#dateFrom').val();
		to = $('#dateTo').val();
		if(from !== undefined && from.length > 0 && 
			to !== undefined && to.length > 0){
			fetchSummaryAjax(new Date(from), new Date(to));
		}
	});
	buildURLFromMonthYearSelects();
});