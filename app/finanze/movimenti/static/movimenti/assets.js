var balanceItemFactory = function(index){
	input = $(`<input type="number" step="0.01" id="balance_item_${index}" onChange="computeSum()"/>`)
	return input;
}
var balanceListItemFactory = function(index) {
	var removebtn = $(`<button type="button" onClick="removeButtonClick(this)" />`)
		.addClass(['col', 'btn', 'btn-light', 'btn-sm', 'remove-button'])
		.attr("data-index", index)
		.html("Remove");
	var inputitem = balanceItemFactory(index).addClass('form-control');
	var inputrow = $('<div class="row">')
		.attr('data-index', index)
		.append($('<div class="col col-6" />').append(inputitem))
		.append($('<div class="col col-6" />').append(removebtn));
	
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
		sum += parseFloat($(el).val());
	});
	$('#sum').html(sum.toFixed(2));
	$('#id_balance').val(sum);
}
var itemscounter = 0;
$(function(){
	var widgetLabel = $('<label for="items">Partials</label>');
	var sumwidget = $('<label for="sum">Total</label><div id="sum" />');
	var addbutton = $('<button type="button" id="addbutton">Add entry</button>')
		.addClass(['btn', 'btn-info', 'btn-sm']);
	var insertItemslist = $('<div id="itemslist">')
		.append(balanceListItemFactory(itemscounter++));
	var insertItemsWidget = $('<div>')
		.addClass('mb-3')
		.append(insertItemslist, addbutton);
	$('button[type="submit"]').before(widgetLabel, insertItemsWidget, sumwidget);

	// Callbacks
	$('#addbutton').click(function(){
		$('#itemslist').append(balanceListItemFactory(itemscounter++));
	});

	var now = new Date().toISOString();
	now = now.replace(/\.\d+Z?$/, '');
	$('[name="date"]').attr('step', 1).val(now);
})