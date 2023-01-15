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
});