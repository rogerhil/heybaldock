var settings = {};

$(window).load(function () {

	loadAddInstruments();
	loadRemoveInstrument();

	$("#add_player").click(function () {
		var $instBlock = $("#all_instruments");
		if ($instBlock.is(":hidden")) {
			var $el = $(this);
			$.ajax({
				url: $(this).attr('url'),
				type: 'post',
				dataType: 'json',
				success: function (data) {
					if (data.success) {
						$instBlock.slideDown();
						$instBlock.html(data.content);
						loadAddInstruments();
					} else {
						alert('Failed to retrieve instruments information.')
					}
				}
			});
		} else {
			$instBlock.slideUp(500, function () {
				fullHeight();
				contentHeightAuto();
			});
		}
	});

	$('#all_instruments').mouseleave(function () {
		$(this).slideUp();
	});

	var $date = $("#id_birth_date");
	$date.attr("readonly", "readonly");
	var options = {
		dateFormat: 'dd/mm/yy',
		changeMonth: true,
		changeYear: true,
		yearRange: "1940:2000"
	};
	$date.datepicker(options);
	$date.datepicker("option", "dateFormat", "dd/mm/yy");

});

function loadAddInstruments() {
	$('#all_instruments ul.photo_list li').click(function () {
		var $el = $(this);
		$.ajax({
			url: $(this).attr('url'),
			type: 'post',
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$("#players").html(data.content);
					loadRemoveInstrument();
					$el.remove();
				} else {
					alert('Failed to add instrument.')
				}
			}
		});
	});
}

function loadRemoveInstrument() {
	$('img.remove_instrument').click(function (e) {
		e.stopPropagation();
		var remove = confirm("Are you sure you want to remove this instrument? WARNING: All songs who has this instrument associated will lost association.");
		if (!remove) return;
		var $el = $(this);
		$.ajax({
			url: $(this).attr('url'),
			type: 'post',
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$el.parent().fadeOut(800, function () {
						$(this).remove();
					});
				} else {
					alert('Failed to remove instrument.')
				}
			}
		});
	});

	$('ul.instrument_image li').mouseover(function () {
		$(this).find('img.remove_instrument').show();
	});

	$('ul.instrument_image li').mouseleave(function () {
		$(this).find('img.remove_instrument').hide();
	});
}