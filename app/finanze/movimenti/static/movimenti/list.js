var applyFilter = function() {
	datefrom = document.getElementById('filter-dateFrom').value;
	dateto = document.getElementById('filter-dateTo').value;
	desc = document.getElementById('filter-description').value;
	cat = document.getElementById('filter-category').value;
	subcat = document.getElementById('filter-subcategory').value;
	filter = {};
	filteritems = []
	changed = false;
	if(datefrom.length > 0){
		date = _myDateFormat(new Date(datefrom));
		filteritems.push("filter=" + encodeURIComponent(`datefrom=${date}`))
		changed = true;
	}
	if (dateto.length > 0) {
		date = _myDateFormat(new Date(dateto));
		filteritems.push("filter=" + encodeURIComponent(`dateto=${date}`))
		changed = true;
	}
	if(cat >= 0){
		filteritems.push("filter=" + encodeURIComponent(`category=${cat}`))
		changed = true;
	}
	if(subcat >= 0){
		filteritems.push("filter=" + encodeURIComponent(`subcategory=${subcat}`))
		changed = true;
	}
	if(desc.length > 0){
		filteritems.push("filter=" + encodeURIComponent(`description=${desc}`))
		changed = true
	}
	filterquery = filteritems.join("&")
	query = "?" + filterquery;
	window.location.search = query;
};

var cleanFilters = function(){
	window.location.search = "";
};
var updateModal = null;
var entryupdated = false;
const hideFeedbackWithID = (elementid) => {
	document.getElementById(elementid).classList.remove('d-flex', 'd-clock');
	document.getElementById(elementid).classList.add('d-none');
};
var updateUpdateModal = function(movement) {
	var form = document.getElementById('updateModalForm');
	form.elements.namedItem('id').value = movement.id;
	form.elements.namedItem('date').value = new Date(movement.date).toISOString().slice(0, -1); // need to remove trailing 'Z'
	form.elements.namedItem('description').value = movement.description;
	form.elements.namedItem('abs_amount').value = Math.abs(parseFloat(movement.amount));
	form.elements.namedItem('category').value = movement.category.id;
	form.elements.namedItem('subcategory').value = movement.subcategory.id;
};
const setupDeleteModal = () => {
	const deleteConfirmationModalElement = document.getElementById('deleteConfirmationModal')
	deleteConfirmationModalElement.addEventListener('hidden.bs.modal', event => {
		if (entryupdated) {
			window.location.reload();
		}
	});
	deleteConfirmationModalElement.addEventListener('show.bs.modal', event => {
		// Button that triggered the modal
		var button = event.relatedTarget
		// Extract info from data-bs-* attributes
		var entryid = button.getAttribute('data-bs-entryId')
		var form = document.getElementById('deleteModalForm');
		form.elements.namedItem("id").value = entryid;
	});
	const deleteConfirmationModalDeleteButton = document.getElementById("deleteConfirmationModalDeleteButton");
	deleteConfirmationModalDeleteButton.addEventListener("click", event => {
		var form = document.getElementById('deleteModalForm');
		var FD = new FormData(form);
		const url = `/movimenti/movement/delete`;
		var XHR = new XMLHttpRequest();
		XHR.addEventListener('load', function () {
			jres = JSON.parse(XHR.responseText);
			if (jres.deleted !== true) {
				feedbackToShow = "deleteFailFeedback";
				fallback = "Error";
				if (jres.message != undefined) {
					message = jres.message;
				} else {
					message = fallback;
				}
				feedbackElement = document.getElementById(feedbackToShow);
				feedbackElement.getElementsByClassName('message')[0].innerHTML = message;
				feedbackElement.classList.remove('d-none');
				feedbackElement.classList.add('d-flex');
			}else{
				deleteConfirmationModal = new bootstrap.Modal(deleteConfirmationModalElement);
				deleteConfirmationModal._isShown = true; // need to set this manually otherwise the hide call won't do anything
				entryupdated = true;
				deleteConfirmationModal.hide();
			}
		});

		// Define what happens in case of an error
		XHR.addEventListener('error', (event) => {
			feedbackElement = document.getElementById('deleteFailFeedback');
			feedbackElement.getElementsByClassName('message')[0].innerHTML = "Server error.";
			feedbackElement.classList.remove('d-none');
			feedbackElement.classList.add('d-flex');
		});
		XHR.open("POST", url);
		XHR.send(FD);
	});
};
var setupUpdateModal = function() {
	updateModal = document.getElementById('updateModal')
	updateModal.addEventListener('hidden.bs.modal', event => {
		if(entryupdated){
			window.location.reload();
		}
	});
	updateModal.addEventListener('show.bs.modal', event => {
		// Button that triggered the modal
		var button = event.relatedTarget
		// Extract info from data-bs-* attributes
		var entryid = button.getAttribute('data-bs-entryId')
		
		// Update the modal's content.
		var url  = `/movimenti/movement/${entryid}`;
		var XHR = new XMLHttpRequest();
		XHR.addEventListener('load', function () {
			responseData = JSON.parse(XHR.responseText);
			if (responseData.movements == undefined) {
				console.log(`Movement ${entryid} not found`);
			} else {
				mov = responseData.movements[0]; // only one
				updateUpdateModal(mov);
				console.log("Movement: " + XHR.responseText);
			}
		});
		XHR.addEventListener('error', function () {
			console.log(XHR.statusText);
		});
		XHR.open("GET", url);
		XHR.send();
	});
	var updateModalSubmit = document.getElementById('updateModalSubmit');
	updateModalSubmit.addEventListener('click', event => {
		var form = document.getElementById('updateModalForm');
		var movid = form.elements.namedItem('id').value;
		var FD = new FormData(form);
		var url = `/movimenti/movement/${movid}`;
		const XHR = new XMLHttpRequest();
		// Define what happens on successful data submission
		XHR.addEventListener('load', function () {
			jres = JSON.parse(XHR.responseText);
			if(jres.updated === true){
				fallback = "Updated";
				feedbackToShow = "updateSuccessFeedback";
				entryupdated = true;
			}else{
				feedbackToShow = "updateFailFeedback";
				fallback = "Error";
			}
			if(jres.message != undefined){
				message = jres.message;
			}else{
				message = fallback;
			}
			feedbackElement = document.getElementById(feedbackToShow);
			feedbackElement.getElementsByClassName('message')[0].innerHTML = message;
			feedbackElement.classList.remove('d-none');
			feedbackElement.classList.add('d-flex');
		});

		// Define what happens in case of an error
		XHR.addEventListener('error', (event) => {
			feedbackElement = document.getElementById('updateFailFeedback');
			feedbackElement.getElementsByClassName('message')[0].innerHTML = "Server error.";
			feedbackElement.classList.remove('d-none');
			feedbackElement.classList.add('d-flex');
		});

		// Set up our request
		XHR.open('POST', url);
		XHR.send(FD);
	});
};
function drawChart(chartbundle) {
	var data = new google.visualization.DataTable(); //arrayToDataTable([
	const datameta = chartbundle.metadata;
	const chartmeta = chartbundle.metadata.chart;
	const chartdata = chartbundle.data;
	header = chartdata[0];
	datalines = chartdata.slice(1).map(item => {
		return [
			new Date(item[0]),
			item[1],
			item[2],
		];
	});
	data.addColumn("date", header[0]);
	data.addColumn("number", header[1]);
	data.addColumn("number", header[2]);
	data.addRows(datalines);

	var options = {
		title: chartmeta.title,
		hAxis: {
			title: chartmeta.xTitle,
			titleTextStyle: { color: '#333' },
			format: "M-Y"
		},
		vAxis: {
			title: chartmeta.yTitle,
			// minValue: 0,
			format: "€###.##",
			viewWindowMode: 'pretty',
			// minValue: datameta.minVal,
			// maxValue: datameta.maxVal,
		}
	};

	var formatter = new google.visualization.NumberFormat(
		{ prefix: '€', decimalSymbol: ",", groupingSymbol: ".", });
	formatter.format(data, 1); // Apply formatter to second column
	formatter.format(data, 2); // Apply formatter to second column

	var chart = new google.visualization.LineChart(document.getElementById('movement_history_chart_div'));
	chart.draw(data, options);
}
window.addEventListener("load", function(){
	var searchParams = new URLSearchParams(window.location.search);
	var timeseries_query_elements = [];
	for(var pair of searchParams.getAll('filter')) {
		innerpair = pair.split('=')
		if(innerpair[0] === 'category'){
			document.getElementById('filter-category').value = innerpair[1];	
		}
		if(innerpair[0] === 'subcategory'){
			document.getElementById('filter-subcategory').value = innerpair[1];	
		}
		if(innerpair[0] === 'description'){
			document.getElementById('filter-description').value = innerpair[1];	
		}
		if (innerpair[0] === 'datefrom') {
			document.getElementById('filter-dateFrom').value = innerpair[1];
			timeseries_query_elements.push(`datefrom=${innerpair[1]}`);
		} 
		if (innerpair[0] === 'dateto') {
			document.getElementById('filter-dateTo').value = innerpair[1];
			timeseries_query_elements.push(`dateto=${innerpair[1]}`);
		}
	}
	if(searchParams.getAll('filter').length > 0){
		var filterCollapsible = new bootstrap.Collapse('#collapseFilter');
		filterCollapsible.show();
	}
	var collapseFilterCollapsibleBlock = document.getElementById('collapseFilter');
	collapseFilterCollapsibleBlock.addEventListener('shown.bs.collapse', event => {
		document.getElementById('clearFiltersButton').classList.remove('d-none');
	});
	collapseFilterCollapsibleBlock.addEventListener('hidden.bs.collapse', event => {
		document.getElementById('clearFiltersButton').classList.add('d-none');
	});
	setupUpdateModal();
	setupDeleteModal();

	google.charts.load('current', { 'packages': ['corechart'] });
	// Set a callback to run when the Google Visualization API is loaded.
	google.charts.setOnLoadCallback(() => {
		var XHR = new XMLHttpRequest();
		XHR.addEventListener('load', function () {
			const responseData = JSON.parse(XHR.responseText);
			drawChart(responseData);
		});
		XHR.addEventListener('error', function () {
			console.log("Error loading tradinghistory");
		});
		XHR.open("GET", `/movimenti/timeseries?${timeseries_query_elements.join("&")}`);
		XHR.send();
	});
});
