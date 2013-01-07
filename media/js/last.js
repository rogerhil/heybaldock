function startCursor() {
	$('body').append('<img style="position:absolute;cursor:none;" id="mycursor" src="/media/img/loading_24.png" />');
	var element = $('body');
	element.css('cursor','none');
	$(element).mousemove(function(e){
		$('#mycursor').css('left', e.clientX + window.scrollX - 5).css('top', e.clientY + window.scrollY - 5);
	});
}

function stopCursor() {
	var element = $('body');
	element.css('cursor','default');
	$('#mycursor').remove();
}


$(window).load(function () {
	fullHeight();
	$('body').ajaxStart(function() {
		startCursor();
	}).ajaxStop(function() {
		stopCursor();
	});
	$(window).scroll(function (e) {
		var $overlay = $("div.pp_overlay");
		if ($overlay.is(":hidden")) return;
		var $image = $overlay.find("div.loading_image");
		$image.css('top', ($(window).height() / 2) + window.scrollY - 100 + "px");
	});
});

function showOverlay(text) {
	var $overlay = $("div.pp_overlay");
	var $image = $overlay.find("div.loading_image");
	var $footer = $("#footer");
	if (text) {
		$overlay.find('span.loading_text').html(text);
	}
	$overlay.show();
	$overlay.css('height', $footer.position().top + 180 + "px");
	$overlay.css('width', $("html").width() + "px");
	$image.css('left', ($(window).width() / 2) - 100 + "px");
	$image.css('top', ($(window).height() / 2) + window.scrollY - 100 + "px");
}

function hideOverlay() {
	$("div.pp_overlay").hide();
}

function updateOverlayProgressBar(value, text) {
	var $overlay = $("div.pp_overlay");
	if (text) {
		$overlay.find('span.loading_text').html(text);
	}
	var $pbar = $overlay.find('div.progress_bar');
	var pos = Math.floor(($pbar.width() * value) / 100);
	$pbar.html(value + '%');
	$pbar.css('background-position', pos);
}

ajax = function (options) {
	var $overlay = $("div.pp_overlay");
	var $image = $overlay.find("div.loading_image");
	var $footer = $("#footer");
	var suc = options.success;
	$overlay.show();
	$overlay.css('height', $footer.position().top + 180 + "px");
	$overlay.css('width', $("html").width() + "px");
	$image.css('left', ($(window).width() / 2) - 100 + "px");
	$image.css('top', ($(window).height() / 2) + window.scrollY - 100 + "px");

	options.success = function (data) {
		$("div.pp_overlay").hide();
		suc(data);
	}
	options.error = function (jqXHR, textStatus, errorThrown) {
		$("div.pp_overlay").hide();
		alert(errorThrown + ": Please try again!");
	}
	$.ajax(options);
}

