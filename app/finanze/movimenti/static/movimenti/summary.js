var selectDate = function(){
	year = $('#select-year').val();
	month = $('#select-month').val();
	basepath = window.location.href.replace(/\?.*$/, "");
	outpath = `${basepath}?year=${year}&month=${month}`;
	window.location.assign(outpath);
}

$(function(){
	$('[data-category]').click(function(event){
		categoryid = $(this).attr('data-category');
		month = parseInt($('#select-month').val());
		year = parseInt($('#select-year').val());
		tomonth = month == 12 ? 1 : month + 1;
		toyear = month == 12 ? year + 1 : year;
		datefrom = `${year}-${month}-01`;
		dateto = `${toyear}-${tomonth}-01`;
		window.location.assign(`/movimenti/list?filter=category%3D${categoryid}&filter=dateto%3D${dateto}&filter=datefrom%3D${datefrom}`);
	});
});