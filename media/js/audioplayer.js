
var newSong;

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
	newSong = new buzz.sound(url);
	var sliding = false;
	$pl.find('.play_pause').removeClass('play').addClass('pause');
	buzz.all().stop();
	$close.unbind('click').click(function () {
		$pl.fadeOut();
		buzz.all().stop();
		newSong.setTime(0);
	});

	$pl.find('div.advanced').unbind('click').bind('click', function (e) {
		e.stopPropagation();
		var $advops = $pl.find('.advanced_controls');
		if ($advops.is(':hidden')) {
			$pl.find('.advanced_controls').slideDown();
		} else {
			$pl.find('.advanced_controls').slideUp();
		}
	});

	$pl.find('.speed_slider').slider({
		stop: function(event, ui) {
			newSong.setSpeed(ui.value / 10);
		},
		slide: function(event, ui) {
			var speed = (ui.value / 10).toFixed(1);
			var $speed = $pl.find('.speed');
			$speed.html(speed);
			$speed.css('margin-left', (speed * 34 + 27) + 'px');
		},
		max: 40,
		min: 5,
		value: 10,
	});

	newSong.unbind("loadeddata").bind("loadeddata", function(e) {
		var song = this;
		var slider = $pl.find('.audio_slider').slider({
			start: function(event, ui) {
				sliding = true;
			},
			stop: function(event, ui) {
				sliding = false;
				song.setTime(ui.value);
			},
			slide: function(event, ui) {
				sliding = true;
				var timer = buzz.toTimer(ui.value);
				var remain = buzz.toTimer(Math.ceil(song.getDuration() - ui.value));
				$pl.find('.time').html(timer);
			},
			max: Math.ceil(song.getDuration()),
			min: 0
		});
		song.play(url);
		song.setTime(0);
		song.trigger('timeupdate');

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
			song.setTime(0);
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