var _myDateFormat = function (date) {
	year = date.getFullYear();
	month = String(date.getMonth() + 1).padStart(2, '0');
	day = String(date.getDate()).padStart(2, '0');
	return `${year}-${month}-${day}`
};

var setNavActiveItem = function(){
	path = window.location.pathname;
	const navbar = document.getElementById("navigationBar");
	if(!navbar || navbar == undefined)
		return;
	const navlinks = navbar.getElementsByClassName('nav-link');
	for(let i = 0; i < navlinks.length; i++){
		let el = navlinks[i];
		let href = el.getAttribute('href');
		if (window.location.href.search(href) >= 0) {
			el.classList.add('active');
		} else {
			el.classList.remove('active');
		}
	}
}
window.addEventListener("load", () =>{
	setNavActiveItem();
	var csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
	const form = document.getElementById('langSelectionForm');
	const menuitems = form.getElementsByTagName("li");
	for(let i = 0; i < menuitems.length; i++){
		let item = menuitems[i];
		item.addEventListener("click", event =>{
			var langurlitem = event.target.attributes['data-language-code'];
			if (langurlitem != undefined) {
				var FD = new FormData(form);
				FD.append("language", langurlitem.value);
				var url = "/i18n/setlang/";
				const XHR = new XMLHttpRequest();
				// Define what happens on successful data submission
				XHR.addEventListener('load', function() {
					window.location.assign(XHR.responseURL);
				});

				// Define what happens in case of an error
				XHR.addEventListener('error', (event) => {
					alert('Oops! Something went wrong.');
				});

				// Set up our request
				XHR.open('POST', url);
				XHR.send(FD);
			}
		});
	}
	// setup pagination
	// keep search params while updating 'page' value only
	var pagcontrols = document.querySelectorAll('div.pagination a[data-page]');
	for (let index = 0; index < pagcontrols.length; index++) {
		const element = pagcontrols[index];
		element.addEventListener("click", event => {
			var el = event.target;
			var page = el.getAttribute('data-page');
			params = new URLSearchParams(window.location.search);
			params.set('page', page);
			window.location.search = params.toString();
		});	
	}
});