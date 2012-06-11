$(window).load(function () {
	var $eventFlyer = $(".event_flyer");
	var $eventDetails = $(".event_details");
	var h1 = $eventFlyer.css("height").replace('px', '');
	$eventDetails.css("height", h1 - 105 + "px");

	$eventFlyer.find('span').prettyPhoto({
		default_width: 1200,
		default_height: 800,
		allow_resize: true
	});

});
