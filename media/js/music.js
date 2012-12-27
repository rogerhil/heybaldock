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

});

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
		url: '/musica/repertorios/' + repertory_id + '/group/add/',
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
			url: '/musica/repertorios/' + repertory_id + '/group/' + group_id + '/remove/',
			type: 'post',
			dataType: 'json',
			success: function (data) {
				if (data.success) {
					$repertory_content.html(data.content);
					loadRepertory();
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
				url: '/musica/repertorios/' + repertory_id + '/group/' + group_id + '/move/',
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

	$('input[name=song_name]').each(newSong);
	$('img.remove_song').click(removeSongFromRepertory);

}

function loadRepertoryGroup(o) {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
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
				url: '/musica/repertorios/' + repertory_id + '/group/' + group_id + '/item/' + item_id + '/move/',
				type: 'post',
				dataType: 'json',
				data: {number: Number(order)},
				success: function (data) {
					if (data.success) {
						$group_content.html(data.content);
						loadRepertoryGroup(o);
						$(o).find('img.remove_song').click(removeSongFromRepertory);
						$(o).find('input[name=song_name]').each(newSong);
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
		url: '/musica/repertorios/' + rid + '/group/' + group_id + '/song/' + sid + '/add/',
		type: 'post',
		dataType: 'json',
		data: {},
		success: function (data) {
			var s;
			if (data.success) {
				$tr = $(data.song_line);
				$tr.addClass(cycleClass);
				$tr.find('img.remove_song').click(removeSongFromRepertory);
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
		url: '/musica/busca/',
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
		url: '/musica/management/album/song/add_to_main_pertory/',
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