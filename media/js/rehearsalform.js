
$(window).load(function () {
	$('#id_band').parent().hide();
	var $date = $("#id_date");
	$date.attr("readonly", "readonly");
	var options = {
		dateFormat: 'yy-mm-dd',
	    timeFormat: 'hh:mm'
	};
	$date.datetimepicker(options);
	$('<span class="helptext"><strong>Abscense payers in this shout: </strong>' + abscencePayers + '</span>').insertAfter($("#id_paid_by"));
});