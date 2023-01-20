// var balanceItemFactory = function(index){
// 	input = $(`<input type="number" step="0.01" id="balance_item_${index}" name="balance_item" onChange="computeSum()"/>`)
// 	return input;
// };
// var balanceLabelItemFactory = function(index){
// 	input = $(`<input type="text" placeholder="description" name="balance_item_key" \
// class="form-control balance_item_key" id="balance_item_key_${index}" onChange="keyItemChange(this)"/>`)
// 	return input;	
// };
var insertNewListItem = function() {
	// var removebtn = $(`<button type="button" onClick="removeButtonClick(this)" />`)
	// 	.addClass(['col', 'btn', 'btn-light', 'btn-sm', 'remove-button'])
	// 	.attr("data-index", index)
	// 	.html('<span class="d-none d-lg-block">Remove</span><span class="d-lg-none"><i class="bi bi-trash"></i></span>');
	// var labelitem = balanceLabelItemFactory(index).addClass('form-control');
	// var inputitem = balanceItemFactory(index).addClass('form-control');
	// var inputrow = $('<div class="row gx-3">')
	// 	.attr('data-index', index)
	// 	.append($('<div class="col col-6" />').append(labelitem))
	// 	.append($('<div class="col col-4" />').append(inputitem))
	// 	.append($('<div class="col col-2" />').append(removebtn));
	
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
}
var removeButtonClick = function(element){
// 	var index = $(element).attr('data-index');
// 	if($('#itemslist input[type="number"]').length > 1){
// 		$(`[data-index="${index}"]`).remove();
// 	}
	index = parseInt(element.getAttribute('data-index'));
	idtoremove = `balance_item_${index}`;
	document.getElementById(idtoremove).remove();

	computeSum();
}
// var insertNewListItem = function(key, value){
// 	newlistitem = balanceListItemFactory(itemscounter++);
// 	if(!key || key == undefined) {
// 		key = "";
// 	}else{
// 		newlistitem.find('input[name="balance_item_key"]').val(key);
// 	}
// 	if(!value || value == undefined) {
// 		value = 0;
// 	}else{
// 		newlistitem.find('input[name="balance_item"]').val(value);
// 	}
// 	$('#itemslist').append(newlistitem);
// 	computeSum();	
// }
var computeSum = function(){
	var sum = 0;
	var numinputs = document.getElementsByName('balance_item_val');
	numinputs.forEach(element => {
		val = parseFloat(element.value)	
		if(! isNaN(val)) sum += val;
	});
	document.getElementById('sum').innerHTML = sum.toFixed(2);
	document.getElementById('id_balance').value = sum;
}
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
var itemscounter = 0;
window.addEventListener("load", function(event) {
	// Callbacks
	var addbutton = document.getElementById('addbutton');
	addbutton.addEventListener("click", function(){
		// newlistitem = balanceListItemFactory(itemscounter++);
		// document.getElementById('itemslist').append(newlistitem);
		// newlistitem.getElementsByName("balance_item_key").last.focus();
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

		// console.log(JSON.stringify(data));
		// $.ajax({
		// 	method: "POST",
		// 	url: url,
		// 	data: JSON.stringify(data),
		// 	contentType: "application/json",
		// 	headers: {'X-CSRFToken': csrftoken},
        // 	mode: 'same-origin', // Do not send CSRF token to another domain.
        // 	success: function (data) {
        // 		err = data.errors;
        // 		if(err.length > 0){
        // 			err.each((idx, el) =>{
        // 				$('#messages').append(`<p class="bg-warning">${err}</p>`);
        // 			})
        // 		}else{
    	// 			$('#messages').append(`<p class="bg-primary text-white">${err}</p>`);
        // 		}
        // 	}
		// });
	});
})