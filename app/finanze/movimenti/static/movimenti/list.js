var applyFilter = function() {
	// body...
	desc = $('#filter-description').val();
	cat = $('#filter-category').val();
	subcat = $('#filter-subcategory').val();
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

$(function(){
	var searchParams = new URLSearchParams(window.location.search);
	for(var pair of searchParams.entries()) {
	   if(pair[0] === 'filter'){
	   		innerpair = pair[1].split('=')
	   		if(innerpair[0] === 'category'){
	   			$('#filter-category').val(innerpair[1]);	
	   		}
	   		if(innerpair[0] === 'subcategory'){
	   			$('#filter-subcategory').val(innerpair[1]);	
	   		}
	   		if(innerpair[0] === 'description'){
	   			$('#filter-description').val(innerpair[1]);	
	   		}
	   }
	}
});