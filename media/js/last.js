$(window).load(function () {
	fullHeight();
});

ajax = function (options) {
	$("div.pp_overlay").show();
	var suc = options.success;
	options.success = function (data) {
		$("div.pp_overlay").hide();
		suc(data);
	}
	$.ajax(options);
}

