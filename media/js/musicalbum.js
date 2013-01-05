$(window).load(function () {
	tempoClick($("div.table_list td.tempo_cel"));
	tonalityClick($("div.table_list td.tonality_cel"));

	// CLICK OUTSIDE
	$('html').click(function (e) {
		if (!($(e.target).hasClass('pretty_select') || $(e.target).parents().hasClass('pretty_select'))) {
			$('.pretty_select').slideUp();
		}
	});
});

function tempoClick($el) {
	$el.click(function (e) {
		e.stopPropagation();
		$("div.pretty_select").hide();
		var $menu = $(this).find("div.pretty_select");
		loadTempoMenu($menu);
	});
}

function tonalityClick($el) {
	$el.click(function (e) {
		e.stopPropagation();
		$("div.pretty_select").hide();
		var $menu = $(this).find("div.pretty_select");
		$menu.slideDown();
		loadTonalityMenu($menu);
	});
}

function loadTempoMenu($menu) {
	var $tr = $menu.parent().parent();
	var url = $tr.attr('changetempourl');
	var songTempo = Number($tr.attr('songtempo') || 120);
	var $tempoBody = $menu.find('.tempo_body');
	if (songTempo < 10) {
		songTempo = 120;
	}
	$menu.slideDown(500, function () {
		$tempoBody.scrollTop((Number(songTempo) - 11) * 30);
	});
	$menu.find('div.option').unbind('click').click('click', function (e) {
		e.stopPropagation();
		var tempo = $(this).attr('tempoid');
		$.ajax({
			url: url,
			type: "post",
			data: {tempo: tempo},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					var $newtr = $(data.content);
					$newtr.insertAfter($tr);
					var cssClass = $tr.hasClass('odd') ? 'odd' : 'even';
					$newtr.addClass(cssClass);
					$tr.remove();
					tempoClick($newtr.find("td.tempo_cel"));
					tonalityClick($newtr.find("td.tonality_cel"));
				} else {
					alert('An error occurred.');
				}
			}
		});
	});
}

function loadTonalityMenu($menu) {
	var $tr = $menu.parent().parent();
	var url = $tr.attr('changetonalityurl');
	$menu.find('span.option').unbind('click').click('click', function (e) {
		e.stopPropagation();
		var tonality = $(this).attr('tonalityid');
		$.ajax({
			url: url,
			type: "post",
			data: {tonality: tonality},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					var $newtr = $(data.content);
					$newtr.insertAfter($tr);
					var cssClass = $tr.hasClass('odd') ? 'odd' : 'even';
					$newtr.addClass(cssClass);
					$tr.remove();
					tempoClick($newtr.find("td.tempo_cel"));
					tonalityClick($newtr.find("td.tonality_cel"));
				} else {
					alert('An error occurred.');
				}
			}
		});
	});
}
