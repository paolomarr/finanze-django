var computeNetGains = function(){
	$('table tbody tr').each((id, el) => {
		date = new Date($(el).find('td[data-name="date"]').attr('data-val'));
		daydiff = (new Date() - date) / (1000 * 60 * 60 * 24);
		quantity = parseFloat($(el).find('td[data-name="quantity"]').html());
		price = parseFloat($(el).find('td[data-name="price"]').html());
		amount = parseFloat($(el).find('td[data-name="amount"]').html());
		currentval = parseFloat($(el).find('td[data-name="currentval"]').html());
		gross_gain = parseFloat($(el).find('td[data-name="gross_gain"]').html());

		taxes = $('input[name="taxes"]').val() / 100;
		inflation = $('input[name="inflation"]').val() / 100;
		transaction = $('input[name="transaction"]').val();
		if(gross_gain > 0){
			net_gain = parseFloat(gross_gain * (1 - taxes) * Math.pow(1 - inflation, daydiff / 360) - transaction).toFixed(2);
		}else{
			net_gain = gross_gain;
		}
		$(el).find('td[data-name="net_gain"]').html(net_gain);
		if(net_gain > 0){
			$(el).find('td[data-name="net_gain"]').addClass('diff').addClass('gain');
		}
	});
}

var orderlist = [];
// onload
// window.addEventListener("load", function() {computeNetGains();});