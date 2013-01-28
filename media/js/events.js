$(window).load(function () {
	loadMetronome($("td.tempo_cel  span.tempo_metronome"));
	if (!event_is_upcoming) {
		$("#map_area").remove();
	}
});