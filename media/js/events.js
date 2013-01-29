$(window).load(function () {
	var $eventFlyer = $(".event_flyer");
	var $eventDetails = $(".event_details");
	$eventDetails.css("height", h1 - 105 + "px");
	if ($eventFlyer.length) {
		var h1 = $eventFlyer.css("height").replace('px', '');
		$eventFlyer.find('span').prettyPhoto({
			default_width: 1200,
			default_height: 800,
			allow_resize: true
		});
	}
	loadMetronome($("td.tempo_cel  span.tempo_metronome"));
	if (!event_is_upcoming) {
		$("#map_area").remove();
	}
});

function deleteEvent() {
	var conf = window.confirm(gettext("Are you sure you want to delete this Event? WARNING: ALL RELATED PHOTOS AND VIDEOS WILL BE LOST!!! the only way to rescue back will be through drafts."));
	if (conf) {
		document.forms.delete_action.submit();
	}
}