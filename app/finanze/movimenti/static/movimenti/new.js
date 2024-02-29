const absAmountPurge = () => {
	const element = document.getElementById("id_abs_amount");
	if(element){
		const curval = element.value;
		element.value = curval.replace(/,/g, ".");
	}
}
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
			absAmountPurge();
			document.forms['newMovementForm'].submit();
		});
	}
	// add a listener to the abs_amount field, to automatically replace unwanted character(s)
	document.getElementById("id_abs_amount")?.addEventListener("change", (event) => {
		absAmountPurge();
	});
});