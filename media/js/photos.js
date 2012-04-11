$(window).load(function () {
	$('ul.photo_album_list li').click(function () {
		window.location = $(this).attr('photoalbum_url');
	});
	if ($.prettyPhoto) {
		$('ul.photo_list li').prettyPhoto({
			default_width: 1200,
			default_height: 800,
			allow_resize: true
		});
	}
});