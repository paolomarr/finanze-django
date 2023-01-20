var refreshRequested = function() {
	var spinner = document.getElementById('refresh-spinner');
	spinner.classList.remove('d-none');
	var url = "/tradinglog/updatecurrentprice?";
	var search = new URLSearchParams();
	document.querySelectorAll('[data-stock]').forEach(element => {
		stockid = element.getAttribute('data-stock');
		search.append("symbol", stockid);
	});
	url += search;
	var XHR = new XMLHttpRequest();
	XHR.addEventListener('load', function () {
		spinner.classList.add('d-none');
		var response = JSON.parse(XHR.responseText);
		// response is an array
		var error = false;
		if(response.results != undefined){
			response.results.forEach(element => {
				if(element.error != undefined){
					error = true;
					/// TODO: write error in GUI
				}
			});
		}
		if(!error){
			window.location.reload();
		}
	});
	XHR.addEventListener('error', function () {
		/// TODO: write error in GUI
	});
	XHR.open("GET", url);
	XHR.send();
// 	var symbols = [];
//                {% for stock in tradedStocks %}symbols.push("symbol={{stock.symbol}}");
//                {% endfor %}
//  url += "?" + symbols.join("&");
//                $('#refresh-spinner').addClass('spinner-loading');
//                $.ajax({
//  url: url,
//                        method: "GET",
//                        success: function (data) {
//                                console.log(data);
//                                window.location.reload();
//                        },
//                        complete: function () {
//                                $('#refresh-spinner').removeClass('spinner-loading');
//                        }
//                });
}
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