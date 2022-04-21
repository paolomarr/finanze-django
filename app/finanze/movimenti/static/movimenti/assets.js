var balanceItemFactory = function(index){
	input = $(`<input type="number" step="0.01" id="balance_item_${index}" name="balance_item" onChange="computeSum()"/>`)
	return input;
};
var balanceLabelItemFactory = function(index){
	input = $(`<input type="text" placeholder="optional label" name="balance_item_key" \
class="form-control balance_item_key" id="balance_item_key_${index}" onChange="keyItemChange(this)"/>`)
	return input;	
};
var balanceListItemFactory = function(index) {
	var removebtn = $(`<button type="button" onClick="removeButtonClick(this)" />`)
		.addClass(['col', 'btn', 'btn-light', 'btn-sm', 'remove-button'])
		.attr("data-index", index)
		.html("Remove");
	var labelitem = balanceLabelItemFactory(index).addClass('form-control');
	var inputitem = balanceItemFactory(index).addClass('form-control');
	var inputrow = $('<div class="row">')
		.attr('data-index', index)
		.append($('<div class="col col-6" />').append(labelitem))
		.append($('<div class="col col-4" />').append(inputitem))
		.append($('<div class="col col-2" />').append(removebtn));
	
	return inputrow;
}
var removeButtonClick = function(element){
	var index = $(element).attr('data-index');
	if($('#itemslist input[type="number"]').length > 1){
		$(`[data-index="${index}"]`).remove();
	}
	computeSum();
}
var computeSum = function(){
	var sum = 0;
	$('#itemslist input[type="number"]').each(function(id, el){
		val = parseFloat($(el).val())
		if(! isNaN(val)) sum += val;
	});
	$('#sum').html(sum.toFixed(2));
	$('#id_balance').val(sum);
}
var getAssetItemsObjects = function(){
	var objects = [];
	$('#itemslist div.row').each(function(id, el){
		keyinput = $(this).find('input').eq(0);
		valueinput = $(this).find('input').eq(1);
		if(keyinput.val() == "")  return;
		key = keyinput.val();
		val = valueinput.val();
		object = {
			"key": key, "val": val
		};
		objects.push(object);
	});
	console.log(objects);
}
var keyItemChange = function(element){
	getAssetItemsObjects();
}
var itemscounter = 0;
$(function(){
	// var widgetLabel = $('<label for="items">Partials</label>');
	// var sumwidget = $('<label for="sum">Total</label><div id="sum" />');
	// var addbutton = $('<button type="button" id="addbutton">Add entry</button>')
	// 	.addClass(['btn', 'btn-info', 'btn-sm']);
	// var insertItemslist = $('<div id="itemslist">')
	// 	.append(balanceListItemFactory(itemscounter++));
	// var insertItemsWidget = $('<div>')
	// 	.addClass('mb-3')
	// 	.append(insertItemslist, addbutton);
	// $('button[type="submit"]').before(widgetLabel, insertItemsWidget, sumwidget);

	// Callbacks
	$('#addbutton').click(function(){
		newlistitem = balanceListItemFactory(itemscounter++);
		$('#itemslist').append(newlistitem);
		newlistitem.find('input').last().focus();
	}).click();

	var now = new Date().toISOString();
	now = now.replace(/\.\d+Z?$/, '');
	$('[name="date"]').attr('step', 1).val(now);
	$('[name="submit"]').click(function(){
		url = $('form').attr('action');
		date = $('[name="date"]').val();
		data = [];
		$('[name="balance_item"]').each( (id,el) => {
			key = $('[name="balance_item_key"]').eq(id).val();
			val = $(el).val();
			data.push({"notes": key, "balance": val, "date": date});
		});
		console.log(JSON.stringify(data));
		// $.ajax({
		// 	method: "POST",
		// 	url: url,
		// 	data: JSON.stringify(data),
		// 	contentType: "application/json",
		// });
	});
})