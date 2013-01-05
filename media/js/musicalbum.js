var song;
DEFAULT_VOLUME = 200;

$(window).load(function () {
	tempoClick($("div.table_list td.tempo_cel"));
	tonalityClick($("div.table_list td.tonality_cel"));

	// CLICK OUTSIDE
	$('html').click(function (e) {
		if (!($(e.target).hasClass('pretty_select') || $(e.target).parents().hasClass('pretty_select'))) {
			$('.pretty_select').slideUp();
			stopMetronome();
		}
	});

	$("#remove_album").click(removeAlbum);
});


function tempoClick($el) {

	//loadMetronome($el.find('span.tempo_metronome'));

	$el.click(function (e) {
		e.stopPropagation();
		var $menu = $(this).find("div.pretty_select");
		if ($menu.is(":hidden")) {
			$("div.pretty_select").hide();
			loadTempoMenu($menu);
		}
	});
}

function tonalityClick($el) {
	$el.click(function (e) {
		e.stopPropagation();
		$("div.pretty_select").hide();
		var $menu = $(this).find("div.pretty_select");
		$menu.slideDown();
		loadTonalityMenu($menu);
	});
}

function loadTempoMenu($menu) {
	var $td = $menu.parent();
	var $tr = $td.parent();
	var url = $tr.attr('changetemposignatureurl');
	var songTempo = Number($tr.attr('songtempo') || 120);
	var $tempoBody = $menu.find('.tempo_body');
	if (songTempo < 10) {
		songTempo = 120;
	}
	$menu.slideDown(500);
	var $t = $td.find('.tempo_metronome');
	startMetronome(Number($t.attr("tempo")), $t.attr("signaturebeats"), $t.parent().find('div.metronome_graphic'));
	$menu.find(".tempo_slider").each(function () {
		var $par = $(this).parent();
		$(this).slider({
			stop: function(event, ui) {
				$par.find('input[name=tempo]').val(ui.value);
				$par.find('div.tempo_display').html(ui.value + ' bpm');
				slideMetronome(ui.value);
			},
			slide: function(event, ui) {
				$par.find('input[name=tempo]').val(ui.value);
				$par.find('div.tempo_display').html(ui.value + ' bpm');
			},
			value: $par.parent().find('input[name=original_tempo]').val() || 120,
			max: 240,
			min: 10
		});
	});
	$menu.find('input.cancel').unbind('click').click('click', function (e) {
		$menu.slideUp();
		stopMetronome();
	});
	$menu.find('input.change_tempo_signature').unbind('click').click('click', function (e) {
		e.stopPropagation();
		var beats = Number($menu.find('input[name=beats]').val());
		var value = Number($menu.find('input[name=value]').val());
		var tempo = Number($menu.find('input[name=tempo]').val());
		if (!value || !beats) return;
		$.ajax({
			url: url,
			type: "post",
			data: {beats: beats, value: value, tempo: tempo},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					var $newtr = $(data.content);
					$newtr.insertAfter($tr);
					var cssClass = $tr.hasClass('odd') ? 'odd' : 'even';
					$newtr.addClass(cssClass);
					$tr.remove();
					tempoClick($newtr.find("td.tempo_cel"));
					tonalityClick($newtr.find("td.tonality_cel"));
					stopMetronome();
				} else {
					alert('An error occurred.');
				}
			}
		});
	});
}

function loadTonalityMenu($menu) {
	var $tr = $menu.parent().parent();
	var url = $tr.attr('changetonalityurl');
	$menu.find('span.option').unbind('click').click('click', function (e) {
		e.stopPropagation();
		var tonality = $(this).attr('tonalityid');
		$.ajax({
			url: url,
			type: "post",
			data: {tonality: tonality},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					var $newtr = $(data.content);
					$newtr.insertAfter($tr);
					var cssClass = $tr.hasClass('odd') ? 'odd' : 'even';
					$newtr.addClass(cssClass);
					$tr.remove();
					tempoClick($newtr.find("td.tempo_cel"));
					tonalityClick($newtr.find("td.tonality_cel"));
				} else {
					alert('An error occurred.');
				}
			}
		});
	});
}

function removeAlbum() {
	var msg = "Are you sure you want to remove this album? WARNING: This action will also remove all songs from repertories related to this album.";
	if (confirm(msg)) {
		$("#remove_album_form").submit();
	}
}