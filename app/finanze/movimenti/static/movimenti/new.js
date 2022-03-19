$(function(){
	$('button').click(function(){
		isMore = $(this).attr('data_more');
		if(isMore && isMore != undefined){
			$('[name="another"]').val("1");
		}
		$('form').submit();
	});
})