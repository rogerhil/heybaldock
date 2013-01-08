var song;
DEFAULT_VOLUME = 200;

$(window).load(function () {
	tempoClick($("div.table_list td.tempo_cel"));
	tonalityClick($("div.table_list td.tonality_cel"));

	// CLICK OUTSIDE
	$('html').click(function (e) {
		if (!($(e.target).hasClass('pretty_select') || $(e.target).parents().hasClass('pretty_select'))) {
			$('.simple_menu').slideUp();
			stopMetronome();
		}
	});

	$("#remove_album").click(removeAlbum);
	loadUploadAudio();
	$("img.add_to_main_repertory").click(addToMainRepertory);
});


function loadUploadAudio() {

	$(document).keydown(function (e) {
		if (e.shiftKey) {
			$(this).find('td[hasaudio=1] .play_audio_area').hide();
			$(this).find('td[hasaudio=1] .upload_audio_area').show();
		} else {
			$(this).find('td[hasaudio=1] .play_audio_area').show();
			$(this).find('td[hasaudio=1] .upload_audio_area').hide();
		}
	});

	$(document).keyup(function (e) {
		if (e.shiftKey) {
			$('td[hasaudio=1] .play_audio_area').hide();
			$('td[hasaudio=1] .upload_audio_area').show();
		} else {
			$('td[hasaudio=1] .play_audio_area').show();
			$('td[hasaudio=1] .upload_audio_area').hide();
		}
	});

	$("div.table_list img.upload_audio").unbind('click').click(function (e) {
		$(this).parent().find('form input[type=file]').trigger('click');
	});
	$("div.table_list img.play_audio").unbind('click').click(function () {
		var url = $(this).attr('audiourl');
		var name = $(this).attr('name');
		playAudio(name, url, $(this));
	});
	var $file = $("div.table_list form input[type=file]");
	$file.fileupload({
		dataType: 'json',
		start: function (e, data) {
			showOverlay("U P L O A D I N G");
		},
		progress: function (e, data) {
			var value = Math.floor((data.loaded / data.total) * 100);
			var kbytes = (data.loaded / (1024 * 1024)).toFixed(1);
			var text = kbytes + " mb of " + (data.total / (1024 * 1024)).toFixed(1) + " mb";
			updateOverlayProgressBar(value, text);
		},
		fail: function (e, data) {
			hideOverlay();
		},
		done: function (e, data) {
			$('td[hasaudio=1] .play_audio_area').show();
			$('td[hasaudio=1] .upload_audio_area').hide();
			var $tr = data.form.parent().parent().parent();
			var $newtr = $(data.result.content);
			$newtr.insertAfter($tr);
			var cssClass = $tr.hasClass('odd') ? 'odd' : 'even';
			$newtr.addClass(cssClass);
			$tr.remove();
			tempoClick($newtr.find("td.tempo_cel"));
			tonalityClick($newtr.find("td.tonality_cel"));
			stopMetronome();
			loadUploadAudio();
			hideOverlay();
			$newtr.find("img.add_to_main_repertory").click(addToMainRepertory);
		}
	});
}

function tempoClick($el) {

	$el.click(function (e) {
		e.stopPropagation();
		var $menu = $(this).find("div.tempo_menu");
		if ($menu.is(":hidden")) {
			$("div.simple_menu").hide();
			loadTempoMenu($menu);
		}
	});
}

function tonalityClick($el) {
	$el.click(function (e) {
		e.stopPropagation();
		var $menu = $(this).find("div.tonality_menu");
		if ($menu.is(':hidden')) {
			$("div.tonality_menu").hide();
			var $menu = $(this).find("div.tonality_menu");
			$menu.slideDown();
			loadTonalityMenu($menu);
		} else {
			$menu.slideUp();
		}
	});
}

function loadTempoMenu($menu) {
	var $td = $menu.parent().parent();
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
			value: $par.parent().parent().parent().find('input[name=original_tempo]').val() || 120,
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
	var $tr = $menu.parent().parent().parent();
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

function addToMainRepertory() {
	var songId = $(this).attr('songid');
	$.ajax({
		url: '/music/album/song/add_to_main_pertory/',
		type: 'post',
		dataType: 'json',
		data: {id: songId},
		success: function (data) {
			if (data.success) {
				alert("Song added to the main repertory successfully!")
			} else {
				alert(data.message)
			}
		}
	});
}
