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
	}, "soundfont/synth_drum-ogg.js");
});

var intervalMetronome;
var metronomeCount = 0;
var signatureBeats = 4;
var $mg;

function metronomeTickTack() {
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
	$el.unbind('mouseover').mouseover(function () {
		startMetronome(Number($(this).attr("tempo")), $(this).attr("signaturebeats"), $(this).parent().find('div.metronome_graphic'));
	});
	$el.unbind('mouseleave').mouseleave(function () {
		stopMetronome();
	});
}

function startMetronome(tempo, beats, $el) {
	signatureBeats = beats;
	tempo = Number(tempo);
	if (!tempo || !beats || tempo < 10) return;
	$mg = $el;
	intervalMetronome = setInterval(function () {metronomeTickTack()}, (1000 * 60) / tempo);
	$mg.fadeIn(300);
}

function stopMetronome() {
	clearInterval(intervalMetronome);
	metronomeCount = 0;
	if ($mg) {
		$mg.find('div.led').removeClass('tick');
		$mg.find('div.led').removeClass('tack');
	}
	$('div.metronome_graphic').fadeOut(300);
}

function slideMetronome(tempo, beats) {
	if (beats) {
		signatureBeats = beats;
	}
	clearInterval(intervalMetronome);
	metronomeCount = 0;
	intervalMetronome = setInterval(function () {metronomeTickTack()}, (1000 * 60) / tempo);
}
