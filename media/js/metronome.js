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

var miditick, miditack, mtick, mtack;

$(window).load(function () {
	MIDI.loadPlugin(function() {
		miditick = function () {MIDI.noteOn(0, 105, 200, 0);};
		miditack = function () {MIDI.noteOn(0, 100, 200, 0);};
	});
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
		//tick.play();
		miditick();
	} else {
		$mg.find('div.led_' + metronomeCount).addClass('tack');
		//tack.play();
		miditack();
	}
	metronomeCount++;
}

function loadMetronome($el) {
	$el.mouseover(function () {
		var t = Number($(this).attr("tempo"));
		signatureBeats = $(this).attr("signaturebeats");
		if (!t || !signatureBeats || t < 10) return;
		var $mg = $(this).parent().find('div.metronome_graphic');
		intervalMetronome = setInterval(function () {metronomeTickTack($mg)}, (1000 * 60) / t);
		$mg.show();
	});
	$el.mouseleave(function () {
		clearInterval(intervalMetronome);
		metronomeCount = 0;
		$(this).parent().find('div.metronome_graphic').hide();
	});
}
