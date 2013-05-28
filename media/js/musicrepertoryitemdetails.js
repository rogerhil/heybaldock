
$(window).load(function () {
	$('a.add_tablature').click(function (e) {
		e.preventDefault();
		e.stopPropagation();
		$("#add_tablature_menu").slideDown();
	});

	$("#add_tablature_menu div.option").click(function () {
		var id = $("#song_details").attr("itemid");
		var instrument_id = $(this).attr("instrumentid");
		var url = $("#add_tablature_menu").attr("addtablatureurl");
		$.ajax({
			type: 'post',
			url: url,
			dataType: 'json',
			data: {instrument_id: instrument_id},
			success: function (data) {
				if (data.success) {
					$("#tablature_holder").html(data.content);
				}
			}
		});
	});

	$("#tablatures_list .tablature_item").click(function () {
		var url = $(this).attr('showtablatureurl');
		$.ajax({
			url: url,
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$("#tablature_holder").html(data.content);
					loadTablature();
				}
			}
		});
	});

	$("#tablatures_list .tablature_item").first().trigger('click');
});

function loadTablature() {
	var $tab = $("#tablature_holder .tablature");
	$tab.find('.edit').click(function () {
		$tab.find('.edition').fadeIn();
		$tab.find('.view').hide();
	});

	$tab.find('a.add_tablature_player').click(function (e) {
		e.preventDefault();
		e.stopPropagation();
		$("#tablature_users_menu").css('top', $(this).position().top + 'px');
		$("#tablature_users_menu").slideDown();
		var $code_line = $(this).parents('li.code_line');
		$("#tablature_users_menu").attr('tablaturelineid', $code_line.attr('id'));
	});

	$('#tablature_users_menu div.option').click(function (e) {
		var $code_line = $("#" + $("#tablature_users_menu").attr('tablaturelineid'));
		var $li = $('<li userid="' + $(this).attr('userid') + '" class="user_code"></li>');
		$li.append('<img src="' + $(this).find('.icon img').attr('src') + '" />');
		$li.append('<input type="text" name="code" value="" />');
		$li.insertBefore($code_line.find('.players li').last());
		$('#tablature_users_menu').slideUp();
	});

	$tab.find('.save').click(function () {
		var $lines = $tab.find('li.code_line');
		var data = [], lyrics, $lis, d;
		$lines.each(function () {
			lyrics = $(this).find('.edition .lyrics input[name=lyrics]').val();
			$lis = $(this).find('.edition li.user_code');
			d = {
				lyrics: lyrics,
				users: []
			};
			$lis.each(function () {
				d.users.push({
					user_id: $(this).attr('userid'),
					code: $(this).find('input[name=code]').val()
				})
			});
			data.push(d)
		});
		var url = $tab.attr('saveurl');
		$.ajax({
			type: 'post',
			url: url,
			data: {data: JSON.stringify(data)},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$("#tablature_holder").html(data.content);
					loadTablature();
				}
			}
		});
	});

	$tab.find('.user_code').each(function () {
		var userid = $(this).attr('userid');
		var src = $('#tablature_users_menu div.option[userid=' + userid +  '] div.icon img').attr('src');
		$(this).find('img').attr('src', src);
	});
}
