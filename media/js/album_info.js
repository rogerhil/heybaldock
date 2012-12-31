
$(window).load(function () {
	var $form = $('form[name=album_info]');
	var $customInfo = $form.find('input[type=button][name=custom_info]');
	$customInfo.click(getAlbumCustom);
	var $fromYear = $("#id_from_year");
	$fromYear.css('display', 'inline');
	$fromYear.css('margin-right', '10px');
	$fromYear.change(function () {
		$(this).parent().find('strong').remove();
		$("<strong>till " + (Number($(this).val()) + 10) + "</strong>").insertAfter($(this));
	});
	$("<strong>till " + (Number($fromYear.val()) + 10) + "</strong>").insertAfter($fromYear);
});

function registerAlbum() {
	var data = {};
	var validTypes = {text: 1, hidden: 1, radio: 1};
	var isValid = true;
	var v, name, type, par, tab;
	var $form = $("#id_custom_form");
	var errors = [];
	$form.find("input").each(function () {
		name = $(this).attr('name');
		type = $(this).attr('type');
		if (validTypes[type] && name) {
			par = $form.find("input[name=" + name + "]").parent();
			tab = par.parents('table.table_choices');
			tab.parent().find("ul.errorlist").remove();
			if (type == 'radio' && !$("input[name=" + name + "][type=radio]").is(":checked")) {
				isValid = false;
				$('<ul class="errorlist"><li>Required</li></ul>').insertBefore(tab);
				errors.push(name);
				return;
			}
			if (type == 'radio' && !$(this).is(":checked")) {
				return;
			}
			v = $(this).val().trim();
			par = $form.find("input[name=" + name + "]").parent();
			par.parent().find("ul.errorlist").remove();
			if (!v) {
				isValid = false;
				$('<ul class="errorlist"><li>Required</li></ul>').insertBefore(par);
				errors.push(name);
				return;
			}
			data[$(this).attr('name')] = v;
		}
	});
	if (!isValid) {
		alert("Please complete all options above!");
		return;
	}
	ajax({
		url: '/musica/management/album/add/register/',
		type: 'post',
		dataType: 'json',
		data: data,
		success: function (data) {
			if (data.success) {
				window.location = data.redirect_url;
			} else {
				alert(data.message);
			}
		}
	});
}


function hideShowItems(o, selectedPositions) {
	var items = $.parseJSON($(o).val());
	var $itemsTable = $(o).parent().parent().parent();
	var pos = $(o).attr('pos');
	if (items.length != selectedPositions.length) {
		$(o).attr('disabled', 'disabled');
		$itemsTable.find('td[pos=' + pos + ']').hide();
	} else {
		$(o).removeAttr('disabled');
		$itemsTable.find('td[pos=' + pos + ']').show();
	}
}

function showDifferences(o) {
	var diff = $.parseJSON($(o).attr('diff'));
	if (!diff) return;
	if (diff.has_difference) {
		var tds = $(o).find('td');
		tds.css('color', 'inherit');
		var baseTitle = '';
		var ctitle = '';
		for (var k = 0; k < tds.length; k++) {
			if ($(tds[k]).is(':hidden')) continue;
			ctitle = $(tds[k]).html().trim();
			if (!baseTitle) {
				baseTitle = ctitle;
				continue;
			}
			if (ctitle != baseTitle) {
				$(tds[k]).css('color', '#AB2727');
			}
		}
	}
}

function composerTooltip(els) {
	var html = "";
	var name, role, el;
	for (var k=0; k < els.length; k++) {
		el = els[k];
		role = "";
		if (el.anv) {
			name = el.anv;
		} else {
			name = el.name
		}
		if (el.role) {
			role = el.role + " ";
		}
		html += "<p>" + role + name + "</p>"
		if (el.join) {
			html += "<p>Join: " + el.join + "</p>"
		}
	}
	return html;
}

function getAlbumCustom() {
	var $form = $('form[name=album_info]');
	var artist = $form.find('input[type=text][name=artist]').val();
	var album = $form.find('input[type=text][name=album]').val();
	var country = $form.find('select[name=country]').val();
	var from_year = $form.find('select[name=from_year]').val();
	var data = {
		artist: artist,
		album: album,
		country: country,
		from_year: from_year
	};
	ajax({
		url: '/musica/management/album/add/custom_form/',
		data: data,
		success: function (data) {
			$('#album_info_results').html(data);
			$('#positions_choices input[type=radio]').click(function () {
				$('#titles_choices').show();
				$('#durations_choices').show();
				$('#composers_choices').show();
				var $table = $(this).parent().parent().parent();
				$table.find('td').css('background', 'url(/media/img/content_bg.png)');
				if ($(this).is(':checked')) {
					var tdpos = $(this).attr('pos');
					var selectedPositions = $.parseJSON($(this).val());
					$('#titles_choices input[type=radio]').each(function () {
						hideShowItems(this, selectedPositions);
					});

					$('#titles_choices tr').each(function () {
						showDifferences(this);
					});

					$('#durations_choices input[type=radio]').each(function () {
						hideShowItems(this, selectedPositions);
					});

					$('#durations_choices tr').each(function () {
						showDifferences(this);
					});

					$('#composers_choices input[type=radio]').each(function () {
						hideShowItems(this, selectedPositions);
						var items = $.parseJSON($(this).val());
						var $itemsTable = $(this).parent().parent().parent();
						var pos = $(this).attr('pos');
						$itemsTable.find('td[pos=' + pos + ']').tooltip({
							content: function () {
								var linepos = $(this).parent().prevAll().length - 1;
								return composerTooltip(items[linepos]);
							}
						});
					});

					$('#composers_choices tr').each(function () {
						showDifferences(this);
					});

					$table.find('td[pos=' + tdpos + ']').css('background', 'url(/media/img/content_bg_2.png)');
				}
			});
			$('#titles_choices').hide();
			$('#titles_choices input[type=radio]').attr("disabled", "disabled");
			$('#durations_choices').hide();
			$('#durations_choices input[type=radio]').attr("disabled", "disabled");
			$('#composers_choices').hide();
			$('#composers_choices input[type=radio]').attr("disabled", "disabled")

			$("#albums_covers").smoothDivScroll({
				mousewheelScrolling: "allDirections",
				manualContinuousScrolling: true,
				autoScrollingMode: "onStart"
			});
			$("#albums_covers .scrollableArea").css("width", "20000px");
			$("#albums_covers img").click(function () {
				$("#albums_covers img").removeClass("selected");
				$(this).addClass("selected");
				$(this).parent().find("input#cover").val($(this).attr("id"));
			});

			$("#artists li").click(function () {
				$("#artists li").removeClass("selected");
				$(this).addClass("selected");
				$(this).parent().find("input#artist_resource_url").val($(this).attr("title"));
			});

			$("#album_titles li").click(function () {
				$("#album_titles li").removeClass("selected");
				$(this).addClass("selected");
				$(this).parent().find("input#album_title").val($(this).attr("title"));
			});

			$("#album_years li").click(function () {
				$("#album_years li").removeClass("selected");
				$(this).addClass("selected");
				$(this).parent().find("input#year").val($(this).attr("title"));
			});

			$("#album_styles li").click(function () {
				var valueList = [];
				if ($(this).hasClass('selected')) {
					$(this).removeClass("selected");
				} else {
					$(this).addClass("selected");
				}
				$("#album_styles li.selected").each(function () {
					valueList.push($(this).attr("title"));
				});
				$(this).parent().find("input#style").val(JSON.stringify(valueList));
			});

			$("#album_genres li").click(function () {
				var valueList = [];
				if ($(this).hasClass('selected')) {
					$(this).removeClass("selected");
				} else {
					$(this).addClass("selected");
				}
				$("#album_genres li.selected").each(function () {
					valueList.push($(this).attr("title"));
				});
				$(this).parent().find("input#genre").val(JSON.stringify(valueList));
			});

			var blocks = ['artists', 'album_titles', 'album_years', 'album_styles', 'album_genres'];
			var b;
			for (var k = 0; k < blocks.length; k++) {
				b = $("#" + blocks[k]  + " li");
				if (b.length == 1) {
					b.trigger('click');
				}
			}
			blocks = ['positions_choices', 'titles_choices', 'durations_choices', 'composers_choices'];
			for (var k = 0; k < blocks.length; k++) {
				b = $("#" + blocks[k]  + " input[type=radio]");
				if (b.length == 1) {
					b.trigger('click');
					b.trigger('click');
				}
			}

			$("#id_register_album").click(registerAlbum);
		}
	});
}
