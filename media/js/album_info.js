
$(window).load(function () {
	var $form = $('form[name=album_info]');
	var $getInfo = $form.find('input[type=button][name=get_info]');
	var $customInfo = $form.find('input[type=button][name=custom_info]');
	$getInfo.click(getAlbumsInfo);
	$customInfo.click(getAlbumCustom);
});

function registerAlbum() {
	var resourceUrl = $(this).parents().find('div.album-actions').attr('resourceurl');
	$.ajax({
		url: '/musica/management/album/add/register/',
		type: 'post',
		dataType: 'json',
		data: {resource_url: resourceUrl},
		success: function (data) {
			console.log(data);
		}
	});
}

function getAlbumsInfo(page) {
	var $form = $('form[name=album_info]');
	var artist = $form.find('input[type=text][name=artist]').val();
	var album = $form.find('input[type=text][name=album]').val();
	var country = $form.find('select[name=country]').val();
	var from_year = $form.find('select[name=from_year]').val();
	var till_year = $form.find('select[name=till_year]').val();
	var track_list_enumeration = $form.find('input[name=track_list_enumeration]').is(":checked");
	var composers_info = $form.find('input[name=composers_info]').is(":checked");
	page = typeof(page) == 'number' ? page : 1;
	var data = {
		artist: artist,
		album: album,
		page: page,
		country: country,
		from_year: from_year,
		till_year: till_year,
		track_list_enumeration: Number(track_list_enumeration),
		composers_info: Number(composers_info)
	};
	$.ajax({
		url: '/musica/management/album/search/',
		data: data,
		success: function (data) {
			$('#album_info_results').html(data);
			$("#albums").find('tr').click(getAlbumResource);
		}
	});
}

function getAlbumCustom(page) {
	var $form = $('form[name=album_info]');
	var artist = $form.find('input[type=text][name=artist]').val();
	var album = $form.find('input[type=text][name=album]').val();
	var country = $form.find('select[name=country]').val();
	var from_year = $form.find('select[name=from_year]').val();
	var till_year = $form.find('select[name=till_year]').val();
	var data = {
		artist: artist,
		album: album,
		country: country,
		from_year: from_year,
		till_year: till_year
	};
	$.ajax({
		url: '/musica/management/album/custom/',
		data: data,
		success: function (data) {
			$('#album_info_results').html(data);
		}
	});
}

function getAlbumResource() {
	var $self = $(this);
	var url = $self.attr('resource');
	var data = {resource_url: url};
	if ($self.next().is('tr.album-resource')) {
		$self.next().find('.album-resource-data').slideToggle('slow');
		return;
	}
	$.ajax({
		url: '/musica/management/album/search/resource/',
		data: data,
		success: function (data) {
			var $content = $('<tr class="album-resource"><td colspan="4"><div class="album-resource-data">' + data + '</div></td></tr>');
			$content.find('.album-resource-data').hide();
			$self.after($content);
			$content.find('.album-resource-data').slideToggle('slow');
			console.log($content.find('input[type=button].register_album'));
			$content.find('input[type=button].register_album').click(registerAlbum);
		}
	});
}