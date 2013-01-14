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