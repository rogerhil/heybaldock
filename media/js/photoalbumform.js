var uploadCount = 0;

$(window).load(function () {
	var $ul = $("form[name=draft_form] ul.draft_fields");
	var photosTitle = gettext("Photos");
	var html = '<label>' + photosTitle + ':</label><input id="fileupload" type="file" name="image" data-url="/fotos/upload/ajax/" multiple>';
	var $photosBlock = $('<li>' + html + '<div class="clear"></div><div class="photos"><ul class="photosul"></ul></div><div class="clear"></div></li>');
	$ul.append($photosBlock);
	var $form = $('form[name=draft_form]');
	var $submit = $form.find('input[type=submit]');
	$submit.attr('disabled', 'disabled');
	$('#fileupload').fileupload({
        dataType: 'json',
		beforeSend: function (e, data) {
			var $uploadBlock = photoBlock(data);
			if ($uploadBlock) {
				uploadCount++;
				$submit.attr('disabled', 'disabled');
			} else {
				return false;
			}
		},
		progress: function (e, data) {
			updateProgressBar(data);
		},
		fail: function (e, data) {
			uploadCount--;
			if (uploadCount == 0) {
				$submit.removeAttr('disabled');
			}
		},
        done: function (e, data) {
			var url = data.result.data.url;
			var urlview = data.result.data.url_view;
			var $uploadBlock = data.data.upload_block;
			var description = $uploadBlock.find('input[name=image_description]').val();
			fillPhotoBlock($uploadBlock, url, urlview, description);
			updateProgressBar(data, 100);
			uploadCount--;
			if (uploadCount == 0) {
				$submit.removeAttr('disabled');
			}
        }
    });
	fullHeight();

	if (window.JS_FIELDS && window.JS_FIELDS.__all__) {
		var all = window.JS_FIELDS.__all__;
		if (all.error) {
			alert(all.error);
		}
	}

	if (window.JS_FIELDS && window.JS_FIELDS.photo && window.JS_FIELDS.photo.length) {
		var photos = window.JS_FIELDS.photo;
		loadPhotos(photos);

	}

});

function loadPhotos(photos) {
	var photo;
	for (var k = 0; k < photos.length; k++) {
		photo = photos[k];
		var $uploadBlock = photoBlock({name: photo.name.value});
		fillPhotoBlock($uploadBlock, photo.url, photo.url_view, photo.description.value);
		doUpdateProgressBar($uploadBlock, 100, gettext('Saved'));
		if (photo.description.error) {
			$description = $uploadBlock.find('div.description input[name=image_description]');
			ajaxErrorMessage(photo.description.error).insertBefore($description);
			$uploadBlock.css('height', '115px');
			$uploadBlock.find('ul.errorlist li').css('margin', '0');
		}
	}
}

function photoBlock(data) {
	var $photosul = $('div.photos ul.photosul');
	var file = data.files ? data.files[0] : undefined;
	var name = file ? file.name : data.name;
	var $li = $('<li class="photo_upload" image="' +  name + '"></li>');
	var $label = $('<label>' + name + '</label>');
	var $pbar = $('<div class="progress_bar">0%</div>');
	var $fsize = $('<div class="file_size">0kb</div>');
	var placeholderText = gettext("Type the image description here...");
	var $description = $('<div class="description"><input type="text" name="image_description" placeholder="' + placeholderText + '" /></div>');
	var $name = $('<input type="hidden" name="image_name" value="' + name + '" />');
	var $preview = $('<div class="preview"></div>');
	var $info = $('<div class="info"></div>');
	var $remove = $('<a class="remove remove_disabled"></a>');
	$remove.click(removeImage);
	$info.append($label);
	$info.append($pbar);
	$info.append($fsize);
	$info.append($description);
	$info.append($name);
	$li.append($info);
	$li.append($preview);
	$li.append($remove);
	$photosul.append($li);
	if (data.data) {
		data.data.upload_block = $li;
	}
	contentHeightAuto();
	fullHeight();
	if (file && file.type.indexOf('image') == -1) {
		$pbar.remove();
		$name.remove();
		$description.remove();
		var msg = gettext("This file is not an image.");
		$label.html($label.html() + '<br/><span class="red">' + msg + '</span>');
		$li.fadeOut(6000);
		return false;
	}
	$('input[placeholder], textarea[placeholder]').placeholder();
	return $li;
}

function fillPhotoBlock(upload_block, url, urlview, description) {
	var $preview = upload_block.find('.preview');
	var $remove = upload_block.find('.remove');
	var $description = upload_block.find('div.description input[name=image_description]');
	var title = gettext("Click to see bigger");
	var $img = $('<img src="' + url + '" title="' + title + '" />');
	var mt;
	$description.val(description);
	$remove.removeClass('remove_disabled');
	$img.load(function () {
		$preview.html('');
		$preview.append($img);
		mt = Math.floor((60 - $img[0].clientHeight) / 2);
		$preview.css('margin-top', mt + 20 + 'px')
	});
	var mout = function () {
		$img.mouseout(function () {
			var $view = $preview.find('div.view');
			$view.animate({
				width: "100%",
				top: 0,
				left: '0',
				opacity: 1
			}, 200, function () {
				$(this).remove();
				$img.click(function () {
					$(this).unbind('click');
					$(this).unbind('mouseout');
					mover();
				});
			});
		});
	};
	var mover = function () {
		var $view = $('<div class="view"></div>');
		var $imgview = $('<img src="' + urlview  + '" />');
		$imgview.css('width', '100%');
		$view.css('opacity',  '0.4');
		$view.append($imgview);
		$preview.append($view);
		$view.animate({
			width: "400%",
			top: mt*2 - 120 + 'px',
			left: '130px',
			opacity: 1
		}, 300, mout);
	};
	$img.click(function () {
		$(this).unbind('click');
		mover();
	});
}

function removeImage() {
	var $self = $(this);
	if ($self.hasClass('remove_disabled')) return;
	var filename = $self.parent().attr('image');
	var postdata = {'image': filename};
	$self.addClass('remove_disabled');
	$.ajax({
		'type': 'post',
		'url': '/fotos/cancel_upload/ajax/',
		'dataType': 'json',
		'data': postdata,
		'success': function (data) {
			if (data.success) {
				$self.parent().slideUp(500, function () {
					$self.parent().remove();
				});
			}
		}
	});
}

function updateProgressBar(data, value) {
	if (!value) {
		value = Math.floor((data.loaded / data.total) * 100);
	}
	var kbytes = Math.floor(data.loaded / 1024);
	doUpdateProgressBar(data.data.upload_block, value, kbytes + 'kb');
}

function doUpdateProgressBar(upload_block, value, kbytes) {
	var $pbar = upload_block.find('.progress_bar');
	var $fsize = upload_block.find('.file_size');
	var pos = Math.floor(($pbar.width() * value) / 100);
	$pbar.html(value + '%');
	$pbar.css('background-position', pos);
	$fsize.html(kbytes);
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
