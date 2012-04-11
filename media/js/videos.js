$(window).load(function () {
	$('ul.video_album_list li').click(function () {
		window.location = $(this).attr('videoalbum_url');
	});
});