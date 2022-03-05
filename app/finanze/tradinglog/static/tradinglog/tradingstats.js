$(document).ready(function(){
	$('.diff').each((id,el) => {
		gain = parseFloat($(el).html());
		if(gain < 0){
			$(el).addClass('loss');
		}else{
			$(el).addClass('gain');
		}
	});
	$('[data-stock]').click(function(event){
		categoryid = $(this).attr('data-stock');
		window.location.assign(`/tradinglog/orders?filter=stock%3D${categoryid}`);
	});
});