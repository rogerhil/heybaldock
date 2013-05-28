$(window).load(function () {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");

	loadRepertory();

	loadRepertoryTrash();

	loadGlobalCancelActions();

	loadSongDetails();
});

function loadRepertory() {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	loadRatings($(".ratings_cel"));
	loadAudio();
	$repertory_content.find('img.player').click(changePlayerButton);
	if (is_editable) {
		$repertory_content.find('input[name=song_name]').each(newSong);
		$repertory_content.find('img.remove_song').click(removeSongFromRepertory);
		$repertory_content.find('img.add_player').click(addPlayerButton);
		tonalityClick($("td.tonality_cel"));
		modeClick($("td.mode_cel"));
		statusClick($("td.status_cel"));
		dateClick($("td.date_cel"));
	}
	calculateTimeTotal();
	loadMetronome($("td.tempo_cel span.tempo_metronome"));
	initSortTable();
	loadRepertoryActions();
}

function loadSongDetails() {
	var $song_details = $("#song_details");
	var repertory_id = $song_details.attr("repertory_id");
	//loadRatings($("div.ratings"));
	loadAudio();
	$song_details.find('img.player').click(changePlayerButton);
	if (is_editable) {
		$song_details.find('img.remove_song').click(removeSongFromRepertory);
		$song_details.find('img.add_player').click(addPlayerButton);
		tonalityClick($("div.tonality"));
		modeClick($("div.mode"));
		statusClick($("div.status"));
		dateClick($("div.date"));
	}
	calculateTimeTotal();
	loadMetronome($("div.tempo span.tempo_metronome"));
	initSortTable();
	loadRepertoryActions();
}

function addPlayerButton() {
	if (!is_editable) {
		alert("You can't make any changes in a locked repertory");
	}
	var $menu = $(this).parent().find('div.players_menu');
	var $el = $(this);
	if ($menu.is(':hidden')) {
		$('div.player_menu').hide();
		$.ajax({
			url: $el.attr('url'),
			type: 'get',
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					if (data.no_players) {
						$menu.html("<p>No more available players!</p>");
						$menu.show();
						$menu.effect('highlight', {mode: 'hide'}, 2000);
					} else {
						$menu.html(data.content);
						$menu.slideDown();
						loadInstrumentsMenu($menu);
					}
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	} else {
		$menu.slideUp();
	}
}

function loadChangePlayerUserOptions(data, $menu, $changeOptions) {
	if (data.no_players) {
		$changeOptions.html('<p style="padding: 5px 10px 5px 10px;">No more available players for this instrument!</p>');
		$changeOptions.css('border-radius', '5px');
		$changeOptions.show();
		$changeOptions.effect('highlight', {mode: 'hide'}, 4000);
	} else {
		$changeOptions.html(data.content);
		$changeOptions.slideDown();
		$changeOptions.find('div.option').click(function () {
			var url = $(this).attr('changeplayeruserurl');
			$changeOptions.slideUp();
			$.ajax({
				url: url,
				type: 'post',
				data: {player_id: $(this).attr('playerid')},
				dataType: 'json',
				success: function (data) {
					ajaxUpdateSongLine(data.item_id);
				}
			});
		});
	}
}

function loadChangeMemberOptions(data, $menu, $changeOptions) {
	$changeOptions.html(data.content);
	$changeOptions.slideDown();
	$changeOptions.find('div.option').click(function () {
		var url = $(this).attr('changememberurl');
		$changeOptions.slideUp();
		$.ajax({
			url: url,
			type: 'post',
			data: {member_id: $(this).attr('memberid')},
			dataType: 'json',
			success: function (data) {
				loadChangePlayerMenu($menu, data);
				ajaxUpdateSongLine(data.item_id);
			}
		});
	});
}

function toogleTagType($menu, o) {
	if (!is_editable) return;
	var $ps = $menu.find('div.pretty_select');
	$.ajax({
		url: $ps.attr('toogletagtypeurl'),
		type: 'post',
		data: {tag_type_id: $(o).attr('tagtypeid')},
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				loadChangePlayerMenu($menu, data);
				if ($(o).hasClass('tag_selected')) {
					$(o).removeClass('tag_selected');
				} else {
					$(o).addClass('tag_selected');
				}
			} else {
				var msg = data.message || "An error occured";
				alert(msg);
			}
		}
	});
}

function setAsLead($menu, playerItemId, playerisLead) {
	if (!is_editable) return;
	$.ajax({
		url: $menu.find('div.pretty_select').attr('setasleadurl'),
		type: 'post',
		data: {is_lead: Number(!playerisLead)},
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				updateSongLine(data);
			} else {
				alert('Could not remove player to this song.');
			}
		}
	});
}

function removePlayerItem($menu, playerItemId) {
	if (!is_editable) return;
	$.ajax({
		url: $menu.find('div.pretty_select').attr('removeplayerurl'),
		type: 'post',
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				updateSongLine(data);
			} else {
				var msg = data.message || "An error occured";
				alert(msg);
			}
		}
	});
}

function loadInstrumentsMenu($menu) {
	$menu.find('div.choose_instrument div.option').click(function () {
		var itemid = $(this).attr('itemid');
		var instrumentid = $(this).attr('instrumentid');
		var isVocal = $(this).attr('instrumentname').toLowerCase() == 'vocal';
		loadPlayersMenu($menu, itemid, instrumentid, isVocal);
	});
}

function loadPlayersMenu($menu, itemid, instrumentid, isVocal) {
	$menu.find('div.choose_instrument').hide();
	$menu.find('div.choose_player div.players_by_instrument_' + instrumentid).show();
	$menu.find('div.choose_player').slideDown();
	$menu.find('div.choose_player div.option').click(function () {
		var playerid = $(this).attr('playerid');
		loadPlayAsMenu($menu, itemid, playerid, instrumentid, isVocal);
	});
}

function loadPlayAsMenu($menu, itemid, playerid, instrumentid, isVocal) {
	if (isVocal) {
		$menu.find('h3.sing').show();
		$menu.find('h3.play').hide();
	} else {
		$menu.find('h3.play').show();
		$menu.find('h3.sing').hide();
	}
	$menu.find('div.choose_player').hide();
	$menu.find('div.play_as').slideDown();
	$menu.find('div.play_as div.option').click(function () {
		var memberid = $(this).attr('memberid');
		loadTagTypeMenu($menu, itemid, playerid, instrumentid, memberid);
	});
}

function loadTagTypeMenu($menu, itemid, playerid, instrumentid, memberid) {
	$menu.find('div.play_as').hide();
	var $tags = $menu.find('div.tags_for_instrument_' + instrumentid);
	if (!$tags.length) {
		addPlayer($menu, itemid, playerid, instrumentid, memberid, []);
		return;
	}
	$tags.slideDown();
	$tags.find('div.tag').click(function () {
		if ($(this).hasClass('tag_selected')) {
			$(this).removeClass('tag_selected');
		} else {
			$(this).addClass('tag_selected');
		}
	});
	$tags.find('input[type=button].add_player').click(function () {
		var tagTypes = [];
		$tags.find('div.tag').each(function () {
			if ($(this).hasClass('tag_selected')) {
				tagTypes.push($(this).attr('tagtypeid'));
			}
		});
		addPlayer($menu, itemid, playerid, instrumentid, memberid, tagTypes);
	});

}

function addPlayer($menu, itemid, playerid, instrumentid, memberid, tagTypes) {
	if (!is_editable) return;
	$menu.slideUp(1000, function () {
		$menu.remove();
	});
	$.ajax({
		url: $menu.attr('addplayerurl'),
		type: 'post',
		data: {player_id: playerid, member_id: memberid, tag_types: tagTypes},
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				updateSongLine(data);
			} else {
				var msg = data.message || "An error occured";
				alert(msg);
			}
		}
	});
}

function tonalityClick($el) {
	if (!is_editable) return;
	$el.unbind('click').click(function (e) {
		e.stopPropagation();
		var $menu = $("#tonality_menu");
		var url = $(this).attr('changetonalityurl');
		$menu.css('left', $(this).position().left - 40 + 'px');
		$menu.css('top', $(this).position().top + 25 + 'px');
		if ($menu.is(":hidden")) {
			$("div.tonality_menu").hide();
			$menu.slideDown();
			loadTonalityMenu($menu, url);
		} else {
			$menu.slideUp();
		}
	});
}

function modeClick($el) {
	if (!is_editable) return;
	$el.unbind('click').click(function (e) {
		e.stopPropagation();
		var $menu = $("#mode_menu");
		var url = $(this).attr('changemodeurl');
		$menu.css('left', $(this).position().left - 40 + 'px');
		$menu.css('top', $(this).position().top + 25 + 'px');
		if ($menu.is(":hidden")) {
			$("div.mode_menu").hide();
			$menu.slideDown();
			loadModeMenu($menu, url);
		} else {
			$menu.slideUp();
		}
	});
}

function statusClick($el) {
	if (!is_editable) return;
	$el.unbind('click').click(function (e) {
		e.stopPropagation();
		var $menu = $("#status_menu");
		var url = $(this).attr('changestatusurl');
		$menu.css('left', $(this).position().left - 20 + 'px');
		$menu.css('top', $(this).position().top + 25 + 'px');
		if ($menu.is(":hidden")) {
			$("div.status_menu").hide();
			$menu.slideDown();
			loadStatusMenu($menu, url);
		} else {
			$menu.slideUp();
		}
	});
}

function dateClick($el) {
	if (!is_editable) return;
	$el.unbind('click').click(function (e) {
		e.stopPropagation();
		var $menu = $("#date_menu");
		var url = $(this).attr('changedateurl');
		var date = $(this).attr('date');
		$menu.css('left', $(this).position().left + 'px');
		$menu.css('top', $(this).position().top + 'px');
		if ($menu.is(":hidden")) {
			$("div.status_menu").hide();
			$menu.show();
			loadDateMenu($menu, url, date);
		} else {
			$menu.hide();
		}
	});
}

function loadModeMenu ($menu, url) {
	if (!is_editable) return;
	$menu.find('div.option').unbind('click').click(function () {
		var mode = $(this).attr("modeid");
		$.ajax({
			url: url,
			type: 'post',
			data: {mode_id: mode},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					updateSongLine(data);
					$menu.slideUp();
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
}

function loadTonalityMenu($menu, url) {
	if (!is_editable) return;
	var $tr = $menu.parent().parent().parent();
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
					updateSongLine(data);
					$menu.slideUp();
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
}

function loadStatusMenu($menu, url) {
	if (!is_editable) return;
	$menu.find('div.option').unbind('click').click(function () {
		var status = $(this).attr("statusid");
		$.ajax({
			url: url,
			type: 'post',
			data: {status_id: status},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					updateSongLine(data);
					$menu.slideUp();
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
}

function loadDateMenu($menu, url, date) {
	if (!is_editable) return;
	var options = {
		dateFormat: 'yy-mm-dd'
	};
	var $input = $menu.find('input');
	$input.val(date);
	$input.datepicker(options);
	$input.unbind('change').change(function () {
		$input.val($(this).val());
		var date = $(this).val();
		$.ajax({
			url: url,
			type: 'post',
			data: {date: date},
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					updateSongLine(data);
					$menu.slideUp();
				} else {
					var msg = data.message || "An error occured";
					alert(msg);
				}
			}
		});
	});
	$input.trigger('focus');
	$menu.hide();
}

function trashAction(url) {
	$.ajax({
		url: url,
		type: 'post',
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				loadRepertoryTrash(data);
				updateRepertoryStats();
			} else {
				alert(data.message || 'An error occurred!');
			}
		}
	});
}

function loadRepertoryTrash(data) {
	var $repertoryTrash = $("#repertory_trash");
	var $repertoryContent = $("#repertory_content");
	if (data) {
		if (data.trash_content) {
			$repertoryTrash.html(data.trash_content);
		}
		if (data.repertory_content) {
			$repertoryContent.html(data.repertory_content);
			loadRepertory();
		}
	}
	var $repertoryTrash = $("#repertory_trash");
	var $repertoryContent = $("#repertory_content");
	$repertoryTrash.find('img.purge_song').click(function () {
		trashAction($(this).attr('purgeurl'));
	});
	$repertoryTrash.find('img.restore_song').click(function () {
		trashAction($(this).attr('restoreurl'));
	});
}
