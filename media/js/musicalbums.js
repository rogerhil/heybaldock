$(window).load(function () {
	var $albums = $("#albums li").click(function () {
		window.location = $(this).attr("url");
	});
});