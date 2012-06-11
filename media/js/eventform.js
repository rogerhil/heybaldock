
$(window).load(function () {
	var $startsat = $("#id_starts_at");
	var $endsat = $("#id_ends_at");
	$endsat.parent().hide();
	$startsat.attr("readonly", "readonly");
	var options = {
		dateFormat: 'yy-mm-dd',
	    timeFormat: 'hh:mm'
	};
	$startsat.datetimepicker(options);
	$startsat.change(function () {
		$endsat.val($(this).val());
	});
});