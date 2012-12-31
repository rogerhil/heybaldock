var settings = {};

$(window).load(function () {
	if ($.prettyPhoto) {
		$('ul.photo_list li').prettyPhoto({
			default_width: 1200,
			default_height: 800,
			allow_resize: true,
			social_tools: ''
		});
	}

	$('ul.photo_album_list li').click(function () {
		window.location = $(this).attr('url');
	});
});
