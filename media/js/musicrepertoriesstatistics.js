$(window).load(function () {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");

	loadRepertory();

	loadGlobalCancelActions();

	loadActions();
});

function loadRepertory() {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	loadRatings($("td.ratings_cel"));
	loadAudio();
	$repertory_content.find('img.player').click(changePlayerButton);
	calculateTimeTotal();
	initSortTable();
	loadRepertoryActions();
}

function loadActions() {
	var $actions = $(".repertories_statistics_actions");
	$actions.find("select.add_songs").change(function () {
		var url = $(this).val();
		var $inputs = $("#repertory_content").find("input[type=checkbox][name=actions]:checked");
		if (!url || !$inputs.length) {
			$(this).val("");
			if (!$inputs.length) {
				alert(gettext("You must select at least one song to add."));
			}
			return;
		}
		var ids = [];
		$inputs.each(function () {
			ids.push($(this).val());
		});
		$.ajax({
			url: url,
			type: 'post',
			data: {items_ids: ids},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					window.location = data.url;
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
	var $repertoryContent = $('#repertory_content');
	var $filterForm = $actions.find('form[name=filter_by]');

	$filterForm.find("input[type=button].submit").unbind('click').click(function () {
		var getData = {
			filter_shows_above: $filterForm.find('select[name=filter_shows_above]').val(),
			filter_shows_below: $filterForm.find('select[name=filter_shows_below]').val(),
			filter_rehearsals_above: $filterForm.find('select[name=filter_rehearsals_above]').val(),
			filter_rehearsals_below: $filterForm.find('select[name=filter_rehearsals_below]').val(),
			filter_ratings_above: $filterForm.find('select[name=filter_ratings_above]').val(),
			filter_ratings_below: $filterForm.find('select[name=filter_ratings_below]').val(),
			filter_date_from: $filterForm.find('input[name=filter_date_from]').val(),
			filter_date_to: $filterForm.find('input[name=filter_date_to]').val(),
			filter_artist: $filterForm.find('input[name=filter_artist]').val(),
			filter_album: $filterForm.find('input[name=filter_album]').val(),
			filter_song: $filterForm.find('input[name=filter_song]').val(),
			filter_status: $filterForm.find('select[name=filter_status]').val(),
			filter_mode: $filterForm.find('select[name=filter_mode]').val()
		};
		var $head = $('table.repertory thead.repertory_head');
		var url = $head.attr('sorturl');
		$.ajax({
			url: url,
			type: 'get',
			dataType: 'json',
			data: getData,
			success: function (data) {
				if (data.success) {
					$repertoryContent.html(data.repertory_content);
					loadRepertory();
					$repertoryContent.effect("highlight", 2000);
				}
			}
		});

	});

	$filterForm.find("input[type=button].clear_filter").unbind('click').click(function () {
		$filterForm.find('select').val('');
		$filterForm.find('input[type=text]').val('');
		$filterForm.find('select[name=filter_shows_below]').val("100");
		$filterForm.find('select[name=filter_rehearsals_below]').val("100");
		$filterForm.find('select[name=filter_ratings_below]').val("5");
		$filterForm.find("input[type=button].submit").trigger('click');
	});

	$("#select_all").unbind("click").click(function () {
		var checked = $(this).attr('ischecked') == 'true';
		$(this).attr('ischecked', String(!checked));
		$repertoryContent.find('input[type=checkbox]').each(function () {
			if (checked) {
				$(this).removeAttr("checked");
			} else {
				$(this).attr("checked", "checked");
			}
		});
	});

	var options = {
		dateFormat: 'dd/mm/yy'
	};
	var $dateFrom = $actions.find("input[type=text][name=filter_date_from]");
	var $dateTo = $actions.find("input[type=text][name=filter_date_to]");
	$dateFrom.datepicker(options);
	$dateTo.datepicker(options);
}