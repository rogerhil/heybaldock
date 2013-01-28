var is_event_repertory = false;

$(window).load(function () {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");

	if (is_editable) {

		$('a.remove_repertory').unbind('click').click(function () {
			var yes = confirm("Are you sure you want to remove this entire event repertory?");
			if (yes) {
				$('form[name=remove_repertory_form]')[0].submit();
			}
		});

	}

	loadRepertory();

	loadGlobalCancelActions();

});

function loadAddSongsByCategoryMenu() {
	var $menu = $("#songs_by_category_menu");
	$("#add_songs_by_category a.add_songs_button").unbind('click').click(function (e) {
		$menu.slideDown();
		e.stopPropagation();
	});
	$menu.find('input[type=button][name=cancel]').unbind('click').click(function (e) {
		$menu.slideUp();
	});
	$menu.find('input[type=button][name=submit]').unbind('click').click(function (e) {
		var $form = $menu.find("form[name=add_songs_by_category_form]");
		var url = $form.attr("addsongsbycategoryurl");
		var postData = {};
		$form.find("select").each(function () {
			postData[$(this).attr('name')] = $(this).val();
		});
		$form.find("input[type=radio]").each(function () {
			if ($(this).is(":checked")) {
				postData[$(this).attr('name')] = $(this).val();
			}
		});
		$.ajax({
			url: url,
			type: 'post',
			dataType: 'json',
			data: postData,
			success: function (data) {
				if (data.success) {
					var $repertory_content = $("#repertory_content");
					$repertory_content.html(data.content);
					loadRepertory();
					$menu.slideUp();
					for (var k = 0; k < data.items_ids.length; k++) {
						var $tr = getTrLineByRepertoryItemId(data.items_ids[k]);
						$tr.effect("highlight", {}, 2000);
					}
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
}

function loadRepertory() {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	loadRatings($("td.ratings_cel"));
	loadAudio();
	$repertory_content.find('img.player').click(changePlayerButton);
	if (is_editable) {
		$repertory_content.find('input[name=song_name]').each(newSong);
		$repertory_content.find('#id_interval').unbind('change').change(addInterval);
		$repertory_content.find('img.remove_song').click(removeSongFromRepertory);
 		timesPlayedClick($repertory_content.find("td.times_played_column"));

		$($repertory_content.find('tbody')).sortable({
			placeholder: "ui-state-highlight",
			handle: ".song_handle",
			tolerance: "pointer",
			stop: function (event, ui) {
				var table = $repertory_content.find('table');
				var tr = ui.item;
				var item_id = tr.attr('itemid');
				var currOrder = tr.attr('order');
				var prevOrder = tr.prev().attr('order');
				var nextOrder = tr.next().attr('order');
				var order;
				if (!prevOrder) {
					order = 1;
				} else {
					if (!nextOrder) {
						order = Number(prevOrder);
					} else {
						order = Number(currOrder) < Number(prevOrder) ? Number(prevOrder) : Number(nextOrder);
					}
				}
				$.ajax({
					url: tr.attr('moveitemurl'),
					type: 'post',
					dataType: 'json',
					data: {order: Number(order)},
					success: function (data) {
						if (data.success) {
							$repertory_content.html(data.content);
							loadRepertory();
						} else {
							var msg = data.message || "An error occured";
							alert(msg);
						}
					}
				});
			}
		});
	}
	calculateTimeTotal();
	loadMetronome($("td.tempo_cel span.tempo_metronome"));
	loadAddSongsByCategoryMenu();
}

function addInterval() {
	if (!$(this).val()) return;
	var $repContent = $("#repertory_content");
	var $body = $repContent.find("tbody");
	var $tr;
	var interval = $(this).val();
	$(this).val('');
	$.ajax({
		url: $(this).attr('addintervalurl'),
		type: 'post',
		dataType: 'json',
		data: {interval: interval},
		success: function (data) {
			if (data.success) {
				$tr = $(data.song_line);
				$tr.find('img.remove_song').click(removeSongFromRepertory);
				$body.append($tr);
				$tr.find('img.player').click(changePlayerButton);
				if (isMainRepertory) {
					$tr.find('img.add_player').click(addPlayerButton);
					tonalityClick($tr.find("td.tonality_cel"));
					modeClick($tr.find("td.mode_cel"));
					statusClick($tr.find("td.status_cel"));
				} else {
					timesPlayedClick($tr.find("td.times_played_column"));
				}
				loadMetronome($("td.tempo_cel span.tempo_metronome"));
				loadAudio();
				loadRatings($tr.find("td.ratings_cel"));
			} else {
				var msg = data.message || "An error occured";
				alert(msg);
			}
		}
	});
}

function timesPlayedClick($el) {
	if (!is_editable) return;
	$el.unbind('click').click(function (e) {
		e.stopPropagation();
		var $menu = $("#times_played_menu");
		var url = $(this).attr('changetimesplayedurl');
		var timesplayed = $(this).attr('timesplayed');
		$menu.css('left', $(this).position().left - 30  +  'px');
		$menu.css('top', $(this).position().top + 25 + 'px');
		if ($menu.is(":hidden")) {
			$("div.times_played_menu").hide();
			$menu.show();
			loadTimesPlayedMenu($menu, url, timesplayed);
		} else {
			$menu.hide();
		}
	});
}

function loadTimesPlayedMenu($menu, url, timesplayed) {
	if (!is_editable) return;
	var $select = $menu.find('select');
	$select.val(timesplayed);
	$select.trigger('focus');
	$select.unbind('change').change(function () {
		var timesplayed = $(this).val();
		$.ajax({
			url: url,
			type: 'post',
			data: {times_played: timesplayed},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					updateSongLine(data);
					$menu.slideUp();
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
}