
var settings = {};

$(window).load(function () {
	$('ul.photo_album_list li').click(function () {
		window.location = $(this).attr('photoalbum_url');
	});
	if ($.prettyPhoto) {
		$('ul.photo_list li').prettyPhoto({
			default_width: 1200,
			default_height: 800,
			allow_resize: true,
			social_tools: ''
		});
	}

	$('img.remove_instrument').click(function (e) {
		e.stopPropagation();
		var remove = confirm("Are you sure you want to remove this instrument? WARNING: All users and songs who has this instrument associated will lost association.");
		if (!remove) return;
		var $el = $(this);
		$.ajax({
			url: $(this).attr('url'),
			type: 'post',
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$el.parent().fadeOut(800, function () {
						$(this).remove();
					});
				} else {
					alert('Failed to remove instrument.')
				}
			}
		});
	});

	$('ul.instrument_image li').mouseover(function () {
		$(this).find('img.remove_instrument').show();
	});
	$('ul.instrument_image li').mouseout(function () {
		$(this).find('img.remove_instrument').hide();
	});
});


function deletePhotoAlbum() {
	var conf = window.confirm(gettext("Are you sure you want to delete this PhotoAlbum? WARNING: ALL RELATED PHOTOS WILL BE LOST!!! the only way to rescue back will be through drafts."));
	if (conf) {
		document.forms.delete_action.submit();
	}
}

