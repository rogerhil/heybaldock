
function playAudio(name, url, $nextto) {
	var $pl = $("#audio_player");
	$pl.fadeIn();
	$pl.css('top', $nextto.position().top + 15 + 'px');
	$pl.css('left', $nextto.position().left + 15 + 'px');
	$pl.draggable({
		handle: "h3"
	});
	var $title = $('<span>' + name + '</span>');
	var $close = $('<div style="float: right; width: 16px;"><img src="/media/img/cross_16.png" /></div>')
	$pl.find('h3').html('');
	$pl.find('h3').append($close);
	$pl.find('h3').append($title);
	var song = new buzz.sound(url);
	var sliding = false;
	$pl.find('.play_pause').removeClass('play').addClass('pause');
	buzz.all().stop();
	$close.unbind('click').click(function () {
		$pl.fadeOut();
		buzz.all().stop();
	});
	song.unbind("loadeddata").bind("loadeddata", function(e) {
		song.play(url);
		var slider = $pl.find('.audio_slider').slider({
			stop: function(event, ui) {
				song.setTime(ui.value);
				sliding = false;
			},
			slide: function(event, ui) {
				sliding = true;
				var timer = buzz.toTimer(ui.value);
				var remain = buzz.toTimer(song.getDuration() - ui.value);
				$pl.find('.time').html(timer);
			},
			max: song.getDuration(),
			min: 0
		});

		song.unbind("timeupdate").bind("timeupdate", function(e) {
			if (sliding) return;
			var timer = buzz.toTimer(this.getTime());
			var remain = buzz.toTimer(this.getDuration() - this.getTime());
			$pl.find('.time').html(timer);
			slider.slider("value", this.getTime());
		});
		$pl.find('.stop').unbind('click').click(function () {
			song.stop();
			$pl.find('.play_pause').removeClass('pause').addClass('play');
			slider.slider("value", 0);
		});
		$pl.find('.play_pause').unbind('click').click(function () {
			song.togglePlay();
			if (song.isPaused()) {
				$pl.find('.play_pause').removeClass('pause').addClass('play');
			} else {
				$pl.find('.play_pause').removeClass('play').addClass('pause');

			}

		});
		$pl.find('.mute').unbind('click').click(function () {
			song.toggleMute();
		});

	});

}