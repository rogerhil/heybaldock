
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

function hideShowItems(o, selectedPositions) {
	var items = $.parseJSON($(o).val());
	var $itemsTable = $(o).parent().parent().parent();
	var pos = $(o).attr('pos');
	if (items.length != selectedPositions.length) {
		$(o).attr('disabled', 'disabled');
		$itemsTable.find('td[pos=' + pos + ']').hide();
	} else {
		$(o).removeAttr('disabled');
		$itemsTable.find('td[pos=' + pos + ']').show();
	}
}

function showDifferences(o) {
	var diff = $.parseJSON($(o).attr('diff'));
	if (!diff) return;
	if (diff.has_difference) {
		var tds = $(o).find('td');
		tds.css('color', 'inherit');
		var baseTitle = '';
		var ctitle = '';
		for (var k = 0; k < tds.length; k++) {
			if ($(tds[k]).is(':hidden')) continue;
			ctitle = $(tds[k]).html().trim();
			if (!baseTitle) {
				baseTitle = ctitle;
				continue;
			}
			if (ctitle != baseTitle) {
				$(tds[k]).css('color', '#AB2727');
			}
		}
	}
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
			$('#positions_choices input[type=radio]').click(function () {
				$('#titles_choices').show();
				$('#durations_choices').show();
				$('#composers_choices').show();
				var $table = $(this).parent().parent().parent();
				$table.find('td').css('background', 'url(/media/img/content_bg.png)');
				if ($(this).is(':checked')) {
					var tdpos = $(this).attr('pos');
					var selectedPositions = $.parseJSON($(this).val());
					$('#titles_choices input[type=radio]').each(function () {
						hideShowItems(this, selectedPositions);
					});

					$('#titles_choices tr').each(function () {
						showDifferences(this);
					});

					$('#durations_choices input[type=radio]').each(function () {
						hideShowItems(this, selectedPositions);
					});

					$('#durations_choices tr').each(function () {
						showDifferences(this);
					});

					$('#composers_choices input[type=radio]').each(function () {
						hideShowItems(this, selectedPositions);
						var items = $.parseJSON($(this).val());
						var $itemsTable = $(this).parent().parent().parent();
						var pos = $(this).attr('pos');
						$itemsTable.find('td[pos=' + pos + ']').unbind('mouseover').mouseover(function () {
							var linepos = $(this).parent().prevAll().length - 1;
							console.log(items[linepos]);
						});
					});

					$('#composers_choices tr').each(function () {
						showDifferences(this);
					});

					$table.find('td[pos=' + tdpos + ']').css('background', 'url(/media/img/content_bg_2.png)');
				}
			});
			$('#titles_choices').hide();
			$('#titles_choices input[type=radio]').attr("disabled", "disabled");
			$('#durations_choices').hide();
			$('#durations_choices input[type=radio]').attr("disabled", "disabled");
			$('#composers_choices').hide();
			$('#composers_choices input[type=radio]').attr("disabled", "disabled")
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