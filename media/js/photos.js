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

function deletePhotoAlbum() {
	var conf = window.confirm(gettext("Are you sure you want to delete this PhotoAlbum? WARNING: ALL RELATED PHOTOS WILL BE LOST!!! the only way to rescue back will be through drafts."));
	if (conf) {
		document.forms.delete_action.submit();
	}
}