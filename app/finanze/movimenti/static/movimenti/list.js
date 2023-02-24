var applyFilter = function() {
	// body...
	desc = document.getElementById('filter-description').value;
	cat = document.getElementById('filter-category').value;
	subcat = document.getElementById('filter-subcategory').value;
	filter = {};
	filteritems = []
	changed = false;
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
var updateUpdateModal = function(movement) {
	var form = document.getElementById('updateModalForm');
	document.getElementsByName('date')[0].value = new Date(movement.date).toISOString().slice(0, -1); // need to remove trailing 'Z'
	document.getElementsByName('description')[0].value = movement.description;
	document.getElementsByName('amount')[0].value = parseFloat(movement.amount);
	document.getElementsByName('category')[0].value = movement.category.id;
	document.getElementsByName('subcategory')[0].value = movement.subcategory.id;
};
var setupUpdateModal = function() {
	var updateModal = document.getElementById('updateModal')
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

		// modalTitle.textContent = `New message to ${recipient}`
		// modalBodyInput.value = recipient
	});
	updateModalSubmit.addEventListener('click', event => {

	});
};
window.addEventListener("load", function(){
	var searchParams = new URLSearchParams(window.location.search);
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
	}
	setupUpdateModal();
});