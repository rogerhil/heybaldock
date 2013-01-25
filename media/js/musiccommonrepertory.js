
function loadGlobalCancelActions() {
	// CLICK OUTSIDE
	$('html').click(function (e) {
		if (!($(e.target).hasClass('simple_menu') || $(e.target).parents().hasClass('simple_menu'))) {
			if ($(this).find('div.notes_area').is(':visible')) {
				return;
			}
			$('.simple_menu').slideUp();
		}
	});

	$(document).keydown(function (e) {
		if (e.keyCode == 27) {
			if ($(this).find('div.notes_area').is(':visible')) {
				return;
			}
			$('.simple_menu').slideUp();
			stopMetronome();
			stopAudio();
		}
	});
}

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

function loadAudio() {
	$("div.table_list img.play_audio").unbind('click').click(function () {
		var url = $(this).attr('audiourl');
		var name = $(this).attr('name');
		playAudio(name, url, $(this));
	});
}

function removeSongFromRepertory() {
	if (!is_editable) {
		alert("You can't make any changes in a locked repertory");
	}
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
				if (isMainRepertory) {
					loadRepertoryTrash(data);
				}
			} else {
				var msg = data.message || "An error occured";
				alert(msg);
			}
		}
	});
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
				if (!is_editable) return;
				removePlayerItem($menu, data.player.id);
				$menu.slideUp();
				break;
			case 'set_as_lead':
				if (!is_editable) return;
				setAsLead($menu, data.player.id, data.player.is_lead);
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
	if (isMainRepertory && is_editable) {
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
	}
	loadRatings($menu.find('div.ratings_player'));
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
	if (is_editable) {
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
}

function loadNotes(playerId, o) {
	var notesArea = $(o).find('div.notes_area');
	notesArea.slideDown();
	$('div.notes_save input.close').click(function (e) {
		e.stopPropagation();
		notesArea.slideUp();
	});
	if (!is_editable) return;
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

function getTrLineByRepertoryItemId(itemId) {
	var $tr = $("#repertory_content tr[itemid=" + itemId + "]");
	return $tr;
}

function getItemId(o) {
	return $(o).parents('tr').attr('itemid');
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
			} else {
				var msg = data.message || "An error occurred";
				alert(msg);
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
	if (is_editable) {
		$newTr.find('img.remove_song').click(removeSongFromRepertory);
		if (isMainRepertory) {
			$newTr.find('img.add_player').click(addPlayerButton);
			tonalityClick($newTr.find("td.tonality_cel"));
			modeClick($newTr.find("td.mode_cel"));
			statusClick($newTr.find("td.status_cel"));
			dateClick($newTr.find("td.date_cel"));
		} else {
			timesPlayedClick($newTr.find("td.times_played_column"));
		}
	}
	$newTr.find('img.player').click(changePlayerButton);
	loadMetronome($("td.tempo_cel span.tempo_metronome"));
	loadRatings($newTr.find("td.ratings_cel"));
	loadAudio();
	if (callback) {
		callback();
	}
}

function loadRatings($els) {
	$els.find('img').unbind('mouseover').mouseover(function (e) {
		if (Number($(this).parent().attr('voted')) && !e.shiftKey) return;
		$(this).attr('src', '/media/img/star_selected_16.png');
		$(this).prevAll().attr('src', '/media/img/star_selected_16.png');
	});
	$els.find('img').unbind('mouseleave').mouseleave(function (e) {
		if ($(this).hasClass('inactive')) {
			$(this).attr('src', '/media/img/star_gray_16.png');
		} else {
			$(this).attr('src', '/media/img/star_16.png');
		}
		$(this).prevAll().each(function () {
			if ($(this).hasClass('inactive')) {
				$(this).attr('src', '/media/img/star_gray_16.png');
			} else {
				$(this).attr('src', '/media/img/star_16.png');
			}
		});
	});
	$els.find('img').unbind('click').click(function (e) {
		if (Number($(this).parent().attr('voted')) && !e.shiftKey) return;
		var url = $(this).parent().attr('ratingurl');
		var data = {
			rate: $(this).attr('rate'),
			is_main: Number(isMainRepertory)
		}
		if (!isMainRepertory) {
			data['event_id'] = getItemId(this);
		}
		$.ajax({
			url: url,
			type: 'post',
			data: data,
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
	});
}

function newSong() {
	if (!is_editable) return;
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
				addNewSong(selected.attr('sid'), $name);
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

function addNewSong(sid, $el) {
	if (!is_editable) return;
	var $repContent = $("#repertory_content");
	var rid = $repContent.attr("repertory_id");
	var $body = $repContent.find("tbody");
	var cycleClass = $body.find('tr').length % 2 != 0? 'even' : 'odd';
	var $tr;
	$.ajax({
		url: $el.attr('addurl'),
		type: 'post',
		dataType: 'json',
		data: {id: sid},
		success: function (data) {
			var s;
			if (data.success) {
				$tr = $(data.song_line);
				$tr.addClass(cycleClass);
				$tr.find('img.remove_song').click(removeSongFromRepertory);
				$body.append($tr);
				$tr.find('img.player').click(changePlayerButton);
				if (isMainRepertory) {
					$tr.find('img.add_player').click(addPlayerButton);
					tonalityClick($tr.find("td.tonality_cel"));
					modeClick($tr.find("td.mode_cel"));
					statusClick($tr.find("td.status_cel"));
				}
				loadMetronome($("td.tempo_cel span.tempo_metronome"));
				loadAudio();
				loadRatings($tr.find("td.ratings_cel"));
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
	if (!is_editable) return;
	var $repCont = $("#repertory_content");
	var $form = $(o).parent().parent();
	var $songsContent = $form.find("div.songs_content");
	var img, name, block, selected, $songBlock;
	$.ajax({
		url: $(o).attr('searchurl'),
		type: 'post',
		dataType: 'json',
		data: {name: name},
		success: function (data) {
			if (data.success) {
				$songsContent.html('');
				$(data.songs).each(function () {
					img = '<div class="icon_image"><img src="' + this.url + '" /></div>';
					name = '<div class="song_name">' + this.artist + ' - ' + this.name + '</div>';
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
						addNewSong($(this).attr('sid'), $(o));
						$(o).val('');
					});
				});
				$songsContent.show();
			} else {
				var msg = data.message || "An error occured";
				alert(msg);
			}
		}
	});
}
