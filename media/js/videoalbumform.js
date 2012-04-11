$(window).load(function () {
	var $input = $("input[type=submit]", "form[name=draft_form]");
	var $videosBlock = $('<div class="videos"><ul class="urls"></ul></div><div class="clear"></div>');
	var $addButton = $('<div class="manage_buttons"><a>Add more url</a></div>');
	$addButton.click(function () {
		addVideo();
	});

	$videosBlock.insertBefore($input);
	if (window.JS_FIELDS && JS_FIELDS.url && JS_FIELDS.url.length) {
		var urls = JS_FIELDS.url;
		for (var k = 0; k < urls.length; k++) {
			addVideo(urls[k].value, urls[k].error);
		}
	} else {
		addVideo();
	}
	$videosBlock = $('form div.videos');
	$videosBlock.append($addButton);
	fullHeight();
});

function addVideo(url, error) {
	var $videosBlock = $('form div.videos');
	var $li = $('<li></li>');
	var $label = $('<label>Url:</label>');
	var $input = $('<input style="width: 410px;" type="text" name="url" />');
	var $del = $('<a><img style="margin-left: 10px; cursor: pointer;" src="/media/img/cross_16.png" /></a>');
	$del.click(function () {
		if ($videosBlock.find('li').length > 1) {
			var $uli = $(this).parent('li');
			var $self = $(this);
			$uli.slideUp(300, function() {
				$self.parent('li').remove();
				fullHeight();
			});
		}
	});
	$input.change(urlValidateAndDetails);
	if (url) {
		$input.val(url);
	}
	if (error) {
		$li.append(errorMessage(error));
	}
	$li.append($label).append($input).append($del).append('<div class="clear"></div>');
	$li.hide();
	$videosBlock.find('ul.urls').append($li);
	if (url) {
		$input.trigger('change');
	}
	fullHeight();
	contentHeightAuto();
	$li.slideDown(300, fullHeight);
}

function errorMessage(msg) {
	var $ul = $('<div><ul class="errorlist"><li>' + msg + '</li></ul></div>');
	return $ul;
}

function clearErrorMessage($input) {
	$input.parent().find('ul.errorlist').remove();
}

function ajaxErrorMessage(msg) {
	var $ul = $('<div><ul class="errorlist ajaxerror"><li>' + msg + '</li></ul></div>');
	return $ul;
}

function clearAjaxErrorMessage($input) {
	$input.parent().find('ul.ajaxerror').remove();
}

function urlValidateAndDetails() {
	var $self = $(this);
	var url = $self.val();
	$.ajax({
		'url': '/videos/url_validate_and_details/ajax/',
		'dataType': 'json',
		'data': {url: url},
		'success': function (data) {
			var $parent = $self.parent();
			if (data.success) {
				clearAjaxErrorMessage($self);
				$self.parent().find('div.ajax_video_details').remove();
				var $details = $('<div class="ajax_video_details"></div>');
				var $info = $('<div class="ajax_video_info"></div>');
				$details.append('<div class="ajax_video_thumbnail"><img src="' + data.info.thumbnail_small + '" /></div>');
				$info.append('<p><strong>' + data.info.title + '</strong></p>')
				$info.append('<p>' + data.info.description + '</p>');
				$info.append('<p><strong>Recorded at: </strong>' + data.info.recorded + '</p>');
				$details.append($info);
				$details.append('<div class="clear"></div>');
				$details.insertAfter($parent.children().last());
			} else {
				if (!$self.parent().find('ul.ajaxerror li').html().indexOf(data.error)) {
					ajaxErrorMessage(data.error).insertBefore($parent.first());
				}
			}
			window.setTimeout(fullHeight, 50);
		}
	});
}