buzz.defaults.preload = true;

var tick, tack;

function loadMetronomeAudio() {
	if (buzz.isOGGSupported()) {
		if (!tick || !tack) {
			tick = new buzz.sound("/media/audio/metronome_tick.ogg");
			tack = new buzz.sound("/media/audio/metronome_tack.ogg");
		}
	} else {
		tick = new buzz.sound("/media/audio/metronome_tick.mp3");
		tack = new buzz.sound("/media/audio/metronome_tack.mp3");
	}
}

loadMetronomeAudio();


$(window).load(function () {
	tempoClick($("div.table_list td.tempo_cel"));
	tonalityClick($("div.table_list td.tonality_cel"));

	// CLICK OUTSIDE
	$('html').click(function (e) {
		if (!($(e.target).hasClass('pretty_select') || $(e.target).parents().hasClass('pretty_select'))) {
			$('.pretty_select').slideUp();
		}
	});

	$("#remove_album").click(removeAlbum);
});

var intervalMetronome;
var metronomeCount = 0;
var signatureBeats = 4;

function metronomeTickTack($mg) {
	loadMetronomeAudio();
	$mg.find('div.led').removeClass('tick');
	$mg.find('div.led').removeClass('tack');
	if (metronomeCount % signatureBeats == 0) {
		metronomeCount = 0;
		$mg.find('div.led_' + metronomeCount).addClass('tick');
		tick.play();
	} else {
		$mg.find('div.led_' + metronomeCount).addClass('tack');
		tack.play();
	}
	metronomeCount++;
}



function tempoClick($el) {

	$el.find('span.tempo_metronome').mouseover(function () {
		var t = $(this).attr("tempo");
		signatureBeats = $(this).attr("signaturebeats");
		if (!t) return;
		t = Number(t);
		var $mg = $(this).parent().find('div.metronome_graphic');
		intervalMetronome = setInterval(function () {metronomeTickTack($mg)}, (1000 * 60) / t);
		$mg.show();
	});
	$el.find('span.tempo_metronome').mouseleave(function () {
		clearInterval(intervalMetronome);
		metronomeCount = 0;
		$(this).parent().find('div.metronome_graphic').hide();
	});

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
	var $tr = $menu.parent().parent();
	var url = $tr.attr('changetempourl');
	var urlsignature = $tr.attr('changesignatureurl');
	var songTempo = Number($tr.attr('songtempo') || 120);
	var $tempoBody = $menu.find('.tempo_body');
	if (songTempo < 10) {
		songTempo = 120;
	}
	$menu.slideDown(500, function () {
		$tempoBody.scrollTop((Number(songTempo) - 11) * 30);
	});
	$menu.find('div.option').unbind('click').click('click', function (e) {
		e.stopPropagation();
		var tempo = $(this).attr('tempoid');
		$.ajax({
			url: url,
			type: "post",
			data: {tempo: tempo},
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
	$menu.find('input.change_signature').unbind('click').click('click', function (e) {
		e.stopPropagation();
		var beats = Number($menu.find('input[name=beats]').val());
		var value = Number($menu.find('input[name=value]').val());
		if (!value || !beats) return;
		$.ajax({
			url: urlsignature,
			type: "post",
			data: {beats: beats, value: value},
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