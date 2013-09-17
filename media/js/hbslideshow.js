var sliderInterval;
function slideSwitch() {
	var $active = $('.slideshow figure.active');

	if ( $active.length == 0 ) $active = $('.slideshow figure:last');

	var $next =  $active.next().length ? $active.next()
		: $('.slideshow figure:first');

	$active.addClass('last-active');

	$next.css({opacity: 0.0})
		.addClass('active')
		.animate({opacity: 1.0}, 1000, function() {
			$active.removeClass('active last-active');
		});
	$active.animate({opacity: 0.0}, 1000);
}

function initSlideShow() {
	$('.slideshow figure').css('opacity', '0');
	$('.slideshow figure:last').css('opacity', '1');
	var time = $('.slideshow').attr('time') || 5;
	sliderInterval = setInterval( "slideSwitch()", time * 1000);
}

$(function() {
	initSlideShow();
});