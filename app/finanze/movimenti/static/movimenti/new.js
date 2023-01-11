window.addEventListener("load", () => {
	const formButtons = document.getElementById('newMovementForm').getElementsByTagName("button");
	for (let i = 0; i < formButtons.length; i++) {
		element = formButtons[i];
		element.addEventListener("click", event => {
			event.preventDefault();
			isMore = event.target.attributes['data_more'];
			if (isMore && isMore != undefined) {
				document.getElementsByName("another")[0].value = "1";
			}
			document.forms['newMovementForm'].submit();
		});
	}
	// $('button').click(function(){
	// 	isMore = $(this).attr('data_more');
	// 	if(isMore && isMore != undefined){
	// 		$('[name="another"]').val("1");
	// 	}
	// 	$('form').submit();
	// });
});