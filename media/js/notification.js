buzz.defaults.preload = true;
var dogWoof = new buzz.sound("/media/audio/dog_woof.mp3");
var intervalNotificationCount;

$(window).load(function () {
	$("#notify_users").unbind("click").click(function () {
		$("#notification_menu").slideDown();
	});
	$("#notification_menu a.cancel").unbind("click").click(function () {
		closeSimpleMenus();
	});
	$("#notification_menu a.notify_button").unbind("click").click(function () {
		var $form = $("#notification_menu form[name=notification_form]");
		var url = $form.attr('notifyurl');
		var postData = {
			notes: $form.find("textarea[name=notes]").val(),
			mail: $form.find("input[name=mail]").is(":checked") ? true : ''
		};
		showOverlay(gettext("S E N D I N G"));
		$.ajax({
			url: url,
			type: 'post',
			dataType: 'json',
			data: postData,
			success: function (data) {
				stopCursor();
				hideOverlay();
				if (data.success) {
					notificationsCountUpdate();
					closeSimpleMenus();
				} else {
					alert(data.message);
				}
			}
		});
	});
	$("#notification_menu a.notify_again").unbind("click").click(function () {
		$("#notification_menu form[name=notification_form]").fadeIn();
	});

	$("#my_notifications").unbind('click').click(function () {
		$menu = $("#my_notifications_menu");
		if ($menu.length) return;
		loadMyNotifications();
	});
	closeActions();
	startNotificationsCountUpdate();

});

function startNotificationsCountUpdate() {
	intervalNotificationCount = window.setInterval(notificationsCountUpdate, 1000 * 20);
}

function stopNotificationsCountUpdate() {
	clearInterval(intervalNotificationCount);
}

function closeActions() {
	// CLICK OUTSIDE

	$('html').click(function (e) {
		if (!($(e.target).hasClass('simple_menu') || $(e.target).parents().hasClass('simple_menu'))) {
			if ($(this).find('div.notes_area').is(':visible')) {
				return;
			}
			closeMyNotificationsMenu();
		}
	});

	$(document).keydown(function (e) {
		if (e.keyCode == 27) {
			if ($(this).find('div.notes_area').is(':visible')) {
				return;
			}
			closeMyNotificationsMenu();
		}
	});
}

function closeMyNotificationsMenu() {
	var $base = $("#my_notifications_base");
	var $menu = $("#my_notifications_menu");
	$menu.slideUp(500, function () {
		$base.html('');
	});
}

function loadMyNotifications(onlyUpdate) {
	var $base = $("#my_notifications_base");
	var url = $("#my_notifications").attr("url");
	$.ajax({
		url: url,
		type: 'get',
		dataType: 'json',
		success: function (data) {
			if (data.success) {
				$base.html(data.content);
				var $menu = $base.find("#my_notifications_menu");
				if (onlyUpdate) {
					$menu.show();
				} else {
					$menu.slideDown();
				}
				$menu.draggable({
					handle: "h3"
				});
				$menu.find('h3.pretty_title').css('cursor', 'pointer');
				initMyNotifications($menu);
			} else {
				alert("Failed to load notifications: " + data.message);
			}
		}
	});
}

function initMyNotifications($menu) {
	$menu.find(".subjects tr").unbind("click").click(function () {
		var $self = $(this);
		var url = $self.attr('url');
		if ($self.hasClass('opened')) {
			$self.next().find('div.content').slideUp(500, function () {
				$self.next().remove();
				$menu.find(".subjects tr").removeClass("opened");
			});
			return;
		}
		$.ajax({
			url: url,
			type: 'get',
			dataType: 'json',
			data: {read: true},
			success: function (data) {
				if (data.success) {
					$menu.find(".subjects tr.message").remove();
					$menu.find(".subjects tr").removeClass("opened");
					$newTr = $('<tr class="message"><td colspan="2"><div class="content" style="display: none; background: #f5f5f5; padding: 5px; border-radius: 5px;">' + data.content + '</div></td></tr>');
					$newTr.insertAfter($self);
					$newTr.find('div.content').slideDown();
					$self.addClass("opened");
					if ($self.hasClass('unread')) {
						notificationsCountUpdate();
					}
					$self.removeClass("unread");

				} else {
					alert(data.message);
				}
			}
		});
	});

	$menu.find("h3 img.close").unbind('click').click(function () {
		closeMyNotificationsMenu();
	});
}

function notificationsCountUpdate() {
	var $myn = $("#my_notifications");
	var $ncount = $myn.find(".notifications_count");
	var url = $myn.attr('urlcount');
	$.ajax({
		url: url,
		type: 'get',
		dataType: 'json',
		success: function (data) {
			if (!data.success) return;
			if (Number(data.count)) {
				$ncount.show();
			} else {
				$ncount.fadeOut(1000, function () {
					$ncount.html('');
				});
				return;
			}
			if (Number(data.count) > Number($ncount.html().trim())) {
				$menu = $("#my_notifications_menu");
				if ($menu.length) {
					loadMyNotifications(true);
				}
				dogWoof.play();
				for (var k = 0; k < 3; k++) {
					$myn.effect("highlight");
					$ncount.effect("highlight");
				}
			}
			$ncount.html(data.count);
		}
	});
}