window.addEventListener("load", function(event) {
	var diffElements = document.getElementsByClassName('diff');
	for(var i = 0; i<diffElements.length;i++){
		el = diffElements[i];
		gain = parseFloat(el.innerText);
		if(gain < 0){
			el.classList.add('loss');
		}else{
			el.classList.add('gain');
		}
	};
	document.querySelectorAll('[data-stock]').forEach(element => {
		element.addEventListener("click", function() {
			categoryid = element.getAttribute('data-stock');
			window.location.assign(`/tradinglog/orders?filter=stock%3D${categoryid}`);
		});
	});
});