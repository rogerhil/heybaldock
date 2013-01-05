$(window).load(function () {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	var $newRepertoryForm = $("#new_repertory_group");

	$("#add_repertory_group").click(function () {
		if ($newRepertoryForm.is(":hidden")) {
			var $name = $newRepertoryForm.find('input[name=new_repertory_group_name]');
			$newRepertoryForm.slideDown()
			$name.focus();
		} else {
			$newRepertoryForm.slideUp()
		}
	});

	var $addRepertoryButton = $newRepertoryForm.find('a');
	var $groupNameInput = $newRepertoryForm.find('input[name=new_repertory_group_name]');

	$groupNameInput.keypress(function(event) {
		if (event.which == 13) {
			event.preventDefault();
			addNewRepertoryGroup();
		}
	});

	$addRepertoryButton.click(function () {
		addNewRepertoryGroup();
	});

	loadRepertory();

	$("#remove_album").click(removeAlbum);

	$("img.add_to_main_repertory").click(addToMainRepertory);

	// CLICK OUTSIDE
	$('html').click(function (e) {
		if (!($(e.target).hasClass('pretty_select') || $(e.target).parents().hasClass('pretty_select'))) {
			if ($(this).find('div.notes_area').is(':visible')) {
				return;
			}
			$('.pretty_select').parent().slideUp();
		}
	});
});

function calculateTimeTotal() {
	var totalSeconds = 0;
	var splited, minutes, seconds;
	var $timeTotal = $("#time_total");
	var $between = $timeTotal.find("select[name=time_between_songs]");
	var secondsBetween = $between.val();
	$between.unbind('change').change(function () {
		calculateTimeTotal();
	});
	$("#repertory_content td.duration").each(function () {
		var value = $(this).html().trim();
		if (!value) return;
		splited = value.split(":");
		minutes = Number(splited[0]);
		seconds = Number(splited[1]);
		totalSeconds += minutes * 60;
		totalSeconds += seconds + Number(secondsBetween);
	});
	splited = String(totalSeconds / 60).split('.');
	minutes = zfill(Number(splited[0]), 2);
	seconds = "00";
	if (splited.length > 1) {
		seconds = zfill(Math.ceil((Number(splited[1].slice(0, 2)) / 100) * 60), 2);
	}
	var total = minutes + ":" + seconds;
	$timeTotal.find("span").html(total);
}

function removeSongFromRepertory() {
	var url = $(this).attr('removeurl');
	var $par;
	var $el = $(this);
	$.ajax({
		url: url,
		type: 'post',
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				$par = $el.parent().parent();
				$par.fadeOut(500, function () {
					var p = $(this).parent();
					$(this).remove();
					var n = $(this).attr("number");
					var count = 0, td;
					var classes = ['odd', 'even']
					p.find('tr').each(function () {
						$(this).removeClass('odd');
						$(this).removeClass('even');
						$(this).addClass(classes[count % 2]);
						count++;
						if (count >= n) {
							$(this).attr("number", count);
							td = $(this).children().first().next();
							td.html(zfill(count, 2));
						}
					});
					calculateTimeTotal();
				});
			}
		}
	});
}

function addNewRepertoryGroup() {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	var $newRepertoryForm = $("#new_repertory_group");
	var $name = $newRepertoryForm.find('input[name=new_repertory_group_name]');
	if (!$name.val().trim()) {
		$name.effect("highlight");
		return;
	}
	$newRepertoryForm.hide();
	$.ajax({
		url: '/music/repertory/' + repertory_id + '/group/add/',
		type: 'post',
		dataType: 'json',
		data: {name: $name.val()},
		success: function (data) {
			if (data.success) {
				$repertory_content.html(data.content);
				loadRepertory();
				$name.val('');
			}
		}
	});
}

function loadRepertory() {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");

	$(".remove_group").click(function () {
		var group_id = $(this).parents().find('table').attr('group_id');
		$.ajax({
			url: '/music/repertory/' + repertory_id + '/group/' + group_id + '/remove/',
			type: 'post',
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$repertory_content.html(data.content);
					loadRepertory();
					calculateTimeTotal();
				}
			}
		});
	});

	$('#repertory_groups').sortable({
		placeholder: "ui-state-highlight",
		handle: ".handle",
		tolerance: "pointer",
		stop: function (event, ui) {
			var group_id = ui.item.find('table').attr('group_id');
			var currOrder = ui.item.find('table').attr('order');
			var prevOrder = ui.item.prev().find('table').attr('order');
			var nextOrder = ui.item.next().find('table').attr('order');
			var order;
			if (!prevOrder) {
				order = 1;
			} else {
				if (!nextOrder) {
					order = Number(prevOrder);
				} else {
					order = Number(currOrder) < Number(prevOrder) ? Number(prevOrder) : Number(nextOrder);
				}
			}
			$.ajax({
				url: '/music/repertory/' + repertory_id + '/group/' + group_id + '/move/',
				type: 'post',
				dataType: 'json',
				data: {order: Number(order)},
				success: function (data) {
					if (data.success) {
						$repertory_content.html(data.content);
						loadRepertory();
					}
				}
			});
		}
	});

	$('#repertory_groups .repertory_group_block').each(function () {
		loadRepertoryGroup(this);
	});
	calculateTimeTotal();
	loadMetronome($("td.tempo_cel span.tempo_metronome"));
}

function addPlayerButton() {
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
					alert("Could not load the players menu.");
				}
			}
		});
	} else {
		$menu.slideUp();
	}
}

function changePlayerButton() {
	var $menu = $(this).parent().parent().find('div.change_player_menu');
	var $el = $(this);
	if ($menu.is(':hidden')) {
		$('div.change_player_menu').hide();
		$.ajax({
			url: $el.attr('changeplayermenuurl'),
			type: 'get',
			dataType: 'json',
			success: function (data) {
				loadChangePlayerMenu($menu, data);
			}
		});
	} else {
		$menu.slideUp();
	}
}

function loadChangePlayerMenu($menu, data, callback) {
	$menu.slideDown();
	$menu.html(data.content);
	var $ps = $menu.find('div.pretty_select');
	var $options = $menu.find('div.option');
	$options.unbind('click').click(function () {
		switch ($(this).attr('action')) {
			case 'remove':
				removePlayerItem(data.player.id);
				$menu.slideUp();
				break;
			case 'set_as_lead':
				setAsLead(data.player.id, data.player.is_lead);
				$menu.slideUp();
				break;
			case 'notes':
				loadNotes(data.player.id, this);
				break;
			case 'documents':
				loadDocuments($menu, this);
				break;
			case 'videos':
				console.log('videos');
				break;
			case 'audio_segments':
				console.log('audio_segments');
				break;
			case 'music_scores':
				console.log('music_scores');
				break;
		}
	});
	$menu.find('div.tag_types div.tag').click(function () {
		toogleTagType($menu, this);
	});
	$menu.find('img.change_as_member').click(function () {
		var $changeOptions = $ps.find('div.change_as_member_options');
		if ($changeOptions.is(':hidden')) {
			$.ajax({
				url: $ps.attr('changeasmemberoptionsurl'),
				type: 'get',
				dataType: 'json',
				success: function (data) {
					loadChangeMemberOptions(data, $menu, $changeOptions);
				}
			});
		} else {
			$changeOptions.slideUp();
		}

	});
	$menu.find('img.change_player_user').click(function () {
		var $changeOptions = $ps.find('div.change_player_user_options');
		if ($changeOptions.is(':hidden')) {
			$.ajax({
				url: $ps.attr('changeplayeruseroptionsurl'),
				type: 'get',
				dataType: 'json',
				success: function (data) {
					loadChangePlayerUserOptions(data, $menu, $changeOptions);
				}
			});
		} else {
			$changeOptions.slideUp();
		}

	});
	var $documentsArea = $menu.find('div.documents_area');
	$menu.find('div.option[action=documents]').mouseover(function () {
		$(this).find('.add_document').show();
	});
	$menu.find('div.option[action=documents]').mouseleave(function () {
		$(this).find('.add_document').hide();
	});
	$menu.find('img.add_document').unbind('click').click(function (e) {
		e.stopPropagation();
		var $file = $menu.find('div.new_document_form input[type=file]');
		$file.fileupload({
			dataType: 'json',
			beforeSend: function (e, data) {
				$documentsArea.show();
			},
			progress: function (e, data) {
				//console.log(data);
			},
			fail: function (e, data) {
				//console.log(data);
			},
			done: function (e, data) {
				loadChangePlayerMenu($menu, data.result, function ($m) {
					loadDocuments($m);
				});
			}
		});
		$file.trigger('click');
	});
	if (callback) {
		callback($menu);
	}
}

function loadDocuments($menu) {
	var $documentsArea = $menu.find('div.documents_area');
	if ($documentsArea.is(':hidden')) {
		$documentsArea.slideDown();
	} else {
		$documentsArea.slideUp();
		return
	}
	$documentsArea.find('h4.secondary_option').unbind('mouseover').mouseover(function () {
		$(this).find('div.remove_document').show();
	});
	$documentsArea.find('h4.secondary_option').unbind('mouseleave').mouseleave(function () {
		$(this).find('div.remove_document').hide();
	});
	$documentsArea.find('div.remove_document').unbind('click').click(function (e) {
		e.stopPropagation();
		var url = $(this).parent().attr('removeurl');
		$.ajax({
			url: url,
			type: 'post',
			dataType: 'json',
			success: function (data) {
				loadChangePlayerMenu($menu, data, function ($m) {
					loadDocuments($m);
				});
			}
		});
	});
}

function loadNotes(playerId, o) {
	var notesArea = $(o).find('div.notes_area');
	notesArea.slideDown();
	loadCLEditor($('textarea.notes'));
	$('div.notes_save input.cancel').click(function (e) {
		e.stopPropagation();
		notesArea.slideUp();
		notesArea.find('textarea.notes').val(notesArea.find('textarea.original_notes').val());
	});
	$('div.notes_save input.save').unbind('click').click(function (e) {
		e.stopPropagation();
		notesArea.slideUp();
		var url = notesArea.attr('saveurl');
		$.ajax({
			url: url,
			type: 'post',
			data: {notes: notesArea.find('textarea.notes').val()},
			dataType: 'json',
			success: function (data) {
				notesArea.find('textarea.original_notes').val(notesArea.find('textarea.notes').val());
			}
		});
	});
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
	var $ps = $menu.find('div.pretty_select');
	$.ajax({
		url: $ps.attr('toogletagtypeurl'),
		type: 'post',
		data: {tag_type_id: $(o).attr('tagtypeid')},
		dataType: 'json',
		success: function (data) {
			loadChangePlayerMenu($menu, data);
			if ($(o).hasClass('tag_selected')) {
				$(o).removeClass('tag_selected');
			} else {
				$(o).addClass('tag_selected');
			}
		}
	});
}

function getTrLineByRepertoryItemId(itemId) {
	var $tr = $("#repertory_content tr[itemid=" + itemId + "]");
	return $tr;
}

function setAsLead(playerItemId, playerisLead) {
	var url = '/music/repertory/player_repertory_item/' + playerItemId + '/set_as_lead/';
	$.ajax({
		url: url,
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

function ajaxUpdateSongLine(itemId, callback) {
	var $tr = getTrLineByRepertoryItemId(itemId);
	var url = $tr.attr('updatesonglineurl');
	$.ajax({
		url: url,
		type: 'get',
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				updateSongLine(data, callback);
			}
		}
	});
}

function updateSongLine(data, callback) {
	var $tr = getTrLineByRepertoryItemId(data.item_id);
	var cssClass = $tr.hasClass('odd') ? 'odd' : 'even';
	var $newTr = $(data.content);
	$newTr.addClass(cssClass);
	$newTr.insertBefore($tr);
	$tr.remove();
	$newTr.find('img.remove_song').click(removeSongFromRepertory);
	$newTr.find('img.add_player').click(addPlayerButton);
	$newTr.find('img.player').click(changePlayerButton);
	tonalityClick($newTr.find("td.tonality_cel"));
	modeClick($newTr.find("td.mode_cel"));
	loadMetronome($("td.tempo_cel span.tempo_metronome"));
	if (callback) {
		callback();
	}
}

function removePlayerItem(playerItemId) {
	var url = '/music/repertory/player_repertory_item/' + playerItemId + '/remove/';
	$.ajax({
		url: url,
		type: 'post',
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
	$menu.slideUp(1000, function () {
		$menu.remove();
	});
	var url = "/music/repertory/repertory_item/" + itemid + "/player/" + playerid + "/add/";
	$.ajax({
		url: url,
		type: 'post',
		data: {member_id: memberid, tag_types: tagTypes},
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				updateSongLine(data);
			} else {
				alert('Could not include player to this song.');
			}
		}
	});
}

function tonalityClick($el) {
	$el.click(function (e) {
		e.stopPropagation();
		var $menu = $(this).find("div.tonality_menu");
		if ($menu.is(":hidden")) {
			$("div.tonality_menu").hide();
			$menu.slideDown();
			loadTonalityMenu($menu);
		} else {
			$menu.slideUp();
		}
	});
}

function modeClick($el) {
	$el.click(function (e) {
		e.stopPropagation();
		var $menu = $(this).find("div.mode_menu");
		if ($menu.is(":hidden")) {
			$("div.mode_menu").hide();
			$menu.slideDown();
			loadModeMenu($menu);
		} else {
			$menu.slideUp();
		}
	});
}

function loadModeMenu ($menu) {
	var url = $menu.attr("changemodeurl");
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
					updateSongLine(data);
				} else {
					alert('An error occurred.');
				}
			}
		});
	});
}

function loadRepertoryGroup(o) {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	$(o).find('input[name=song_name]').each(newSong);
	$(o).find('img.remove_song').click(removeSongFromRepertory);
	$(o).find('img.add_player').click(addPlayerButton);
	$(o).find('img.player').click(changePlayerButton);
	tonalityClick($("td.tonality_cel"));
	modeClick($("td.mode_cel"));
	
	$($(o).find('tbody')).sortable({
		placeholder: "ui-state-highlight",
		handle: ".song_handle",
		tolerance: "pointer",
		stop: function (event, ui) {
			var $group_content = $(o);
			var table = $group_content.find('table');
			var group_id = table.attr('group_id');
			var tr = ui.item;
			var item_id = tr.attr('itemid');
			var currOrder = tr.attr('number');
			var prevOrder = tr.prev().attr('number');
			var nextOrder = tr.next().attr('number');
			var order;
			if (!prevOrder) {
				order = 1;
			} else {
				if (!nextOrder) {
					order = Number(prevOrder);
				} else {
					order = Number(currOrder) < Number(prevOrder) ? Number(prevOrder) : Number(nextOrder);
				}
			}
			$.ajax({
				url: '/music/repertory/' + repertory_id + '/group/' + group_id + '/item/' + item_id + '/move/',
				type: 'post',
				dataType: 'json',
				data: {number: Number(order)},
				success: function (data) {
					if (data.success) {
						$group_content.html(data.content);
						loadRepertoryGroup(o);
					}
				}
			});
		}
	});
}

function newSong() {
	var group_id = $(this).parents().find('table').attr('group_id');
	var $name = $(this);
	$name.unbind('keypress').keypress(function(event) {
		var $form = $(this).parent().parent();
		var $songsContent = $form.find("div.songs_content");
		switch (event.which) {
			case 13:
				event.preventDefault();
				selected = $songsContent.find('div.selected');
				if (!selected.length) {
					return;
				}
				$songsContent.hide();
				$songsContent.html('');
				addNewSong(group_id, selected.attr('sid'), $name);
				$(this).val('');
				break;
		}
	});

	$name.unbind('keyup').keyup(function(event) {
		var name = $(this).val();
		var $form = $(this).parent().parent();
		var $songsContent = $form.find("div.songs_content");
		var selected;
		switch (event.which) {
			case 38:
				event.preventDefault();
				selected = $songsContent.find('div.selected');
				if (!selected.length) {
					$songsContent.find('div.song_block').removeClass('selected');
					$songsContent.find('div.song_block').last().addClass('selected');
				} else {
					$songsContent.find('div.song_block').removeClass('selected');
					selected.prev().addClass('selected');
				}
				break;
			case 40:
				event.preventDefault();
				selected = $songsContent.find('div.selected');
				if (!selected.length) {
					$songsContent.find('div.song_block').removeClass('selected');
					$songsContent.find('div.song_block').first().addClass('selected');
				} else {
					$songsContent.find('div.song_block').removeClass('selected');
					selected.next().addClass('selected');
				}
				break;
			case 13:
				break;
			default:
				matchSong(name, this);
				break;
		}
	});
}

function addNewSong(group_id, sid, $el) {
	var $repContent = $("#repertory_content");
	var rid = $repContent.attr("repertory_id");
	var $groups = $("#repertory_groups");
	var $group = $groups.find("table[group_id=" + group_id + "]");
	var $body = $group.find("tbody");
	var cycleClass = $body.find('tr').length % 2 != 0? 'even' : 'odd';
	var $tr;
	$.ajax({
		url: '/music/repertory/' + rid + '/group/' + group_id + '/song/' + sid + '/add/',
		type: 'post',
		dataType: 'json',
		data: {},
		success: function (data) {
			var s;
			if (data.success) {
				$tr = $(data.song_line);
				$tr.addClass(cycleClass);
				$tr.find('img.remove_song').click(removeSongFromRepertory);
				$tr.find('img.add_player').click(addPlayerButton);
				$tr.find('img.player').click(changePlayerButton);
				tonalityClick($tr.find("td.tonality_cel"));
				modeClick($tr.find("td.mode_cel"));
				loadMetronome($("td.tempo_cel span.tempo_metronome"));
				$body.append($tr);
			} else {
				var $msg = $el.parent().find('span.message');
				$msg.html(data.message);
				$msg.fadeIn(500, function () {
					window.setTimeout(function () {
						$msg.fadeOut();
					}, 1000);
				});
				$body.find('tr').each(function () {
					if ($(this).attr('songid') == sid) {
						$(this).effect("highlight", {}, 2000);
					}
				});
			}
			calculateTimeTotal();
		}
	});

}

function matchSong(name, o) {
	var $repCont = $("#repertory_content");
	var $form = $(o).parent().parent();
	var group_id = $form.parent().find('table').attr('group_id')
	var $songsContent = $form.find("div.songs_content");
	var img, name, block, selected, $songBlock;
	$.ajax({
		url: '/music/busca/',
		type: 'post',
		dataType: 'json',
		data: {name: name, group_id: group_id, main: Number($repCont.attr('main'))},
		success: function (data) {
			if (data.success) {
				$songsContent.html('');
				$(data.songs).each(function () {
					img = '<div class="icon_image"><img src="' + this.url + '" /></div>';
					name = '<div class="song_name">' + this.name + '</div>';
					block = '<div class="song_block" sid="' + this.id + '">' + img + name + '</div>'
					$songsContent.append($(block));
					selected = $songsContent.find('div.selected');
					$songBlock = $songsContent.find('div.song_block');
					if (!selected.length) {
						$songBlock.removeClass('selected');
						$songBlock.first().addClass('selected');
					}
					$songBlock.unbind('click').click(function () {
						$songsContent.hide();
						$songsContent.html('');
						addNewSong(group_id, $(this).attr('sid'), $(o));
						$(o).val('');
					});
				});
				$songsContent.show();
			}
		}
	});
}

function removeAlbum() {
	var msg = "Are you sure you want to remove this album? WARNING: This action will also remove all songs from repertories related to this album.";
	if (confirm(msg)) {
		$("#remove_album_form").submit();
	}
}

function addToMainRepertory() {
	var songId = $(this).attr('songid');
	$.ajax({
		url: '/music/album/song/add_to_main_pertory/',
		type: 'post',
		dataType: 'json',
		data: {id: songId},
		success: function (data) {
			if (data.success) {
				alert("Song added to the main repertory successfully!")
			} else {
				alert(data.message)
			}
		}
	});
}