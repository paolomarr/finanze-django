var setNavActiveItem = function(){
	path = window.location.pathname;
	const navlinks = Array.from(document.getElementsByClassName('nav-link'));
	for(let i = 0; i < navlinks.length; i++){
		let el = navlinks[i];
		let href = el.getAttribute('href');
		try {
			let url = new URL(href);
			if (path.search(url.pathname) >= 0) {
				el.classList.add('active');
			} else {
				el.classList.remove('active');
			}
		} catch (error) {
			
		}
	}
}
window.addEventListener("load", () =>{
	setNavActiveItem();
	var csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
	const form = document.getElementById('langSelectionForm');
	const menuitems = document.getElementById("langSelectionMenu").getElementsByTagName("li")
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
				XHR.addEventListener('load', (event) => {
					alert('Yeah! Data sent and response loaded.');
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