$(window).load(function () {
	var $dashboard = $("#dashboard");
	$dashboard.find("div.dashboard_item").click(function () {
		window.location = $(this).attr('url');
	});

});