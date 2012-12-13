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

});


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

	$('a.add_song').click(function () {
		var group_id = $(this).parents().find('table').attr('group_id');
		var $form = $(this).parent().find('div.add_song_form');
		var $name = $form.find('input[name=song_name]');
		var $addButton = $form.find('a');
		if ($form.is(":hidden")) {
			$form.slideDown();
		} else {
			$form.slideUp();
		}

		$name.unbind('keypress').keypress(function(event) {
			if (event.which == 13) {
				event.preventDefault();
				addNewSong(group_id, $name.val());
			}
		});

		$name.unbind('keyup').keyup(function(event) {
			var name = $(this).val();
			matchSong(name);
		});

		$addButton.unbind('click').click(function () {
			addNewSong(group_id, $name.val());
		});

	});

}

function addNewSong(group_id, name) {
	//console.log(group_id);
	//console.log(name);
}

function matchSong(name) {
	$.ajax({
		url: '/musica/busca/',
		type: 'post',
		dataType: 'json',
		data: {name: name},
		success: function (data) {
			if (data.success) {
				console.log(data);
			}
		}
	});
}