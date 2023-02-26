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
var updateModal = null;
var entryupdated = false;
var hideFeedbackWithID = function(elementid) {
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

		// modalTitle.textContent = `New message to ${recipient}`
		// modalBodyInput.value = recipient
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