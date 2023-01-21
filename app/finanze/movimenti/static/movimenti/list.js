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
});