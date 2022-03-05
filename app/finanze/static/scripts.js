var setNavActiveItem = function(){
	path = window.location.pathname;
	$('.nav-link').each((id,el) => {
		let url = new URL($(el).prop('href'));
		if(url.pathname === path ){
			$(el).addClass('active');
		}else{
			$(el).removeClass('active');
		}
	});
}
$(document).ready(function(){
	setNavActiveItem();
});