var setNavActiveItem = function(){
	path = window.location.pathname;
	$('.nav-link').each((id,el) => {
		let url = new URL($(el).prop('href'));
		if(path.search (url.pathname) >= 0 ){
			$(el).addClass('active');
		}else{
			$(el).removeClass('active');
		}
	});
}
$(document).ready(function(){
	setNavActiveItem();
});