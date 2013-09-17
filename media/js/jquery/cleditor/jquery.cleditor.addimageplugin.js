/**
 @preserve CLEditor CMS Plugin v0.0.1
 requires CLEditor v1.2.2 or later

 Copyright 2011, Rogerio Hilbert
*/

// ==ClosureCompiler==
// @compilation_level SIMPLE_OPTIMIZATIONS
// @output_file_name jquery.cleditor.addimageplugin.min.js
// ==/ClosureCompiler==

(function($) {

	// Define the table button
	$.cleditor.buttons.addimage = {
		name: "addimage",
		image: "instagram-icon.png",
		title: "Insert Image",
		command: "inserthtml",
		popupName: "addimage",
		popupClass: "cleditorPrompt",
		popupContent: buildPopupContent(),
		buttonClick: addImageButtonClick
	};

	// Add the button to the default controls
	$.cleditor.defaultOptions.controls += ' addimage';

	function imageTag(url) {
		var $img = $('<img src="' + url + '" />');
		$img.css('height', '80px');
		var $div = $('<div class="item"></div>');
		return $div.append($img);
	}

	function buildPopupContent() {
		load();
		var ul = $('<ul class="wysiwyg_box"></ul>');
		var li = $('<li></li>');
		li.css('max-height', '250px');
		li.css('overflow', 'auto');
		for (var k = 0; k < IMAGES_URLS.length; k++) {
			li.append(imageTag(IMAGES_URLS[k]));
		}
		ul.append(li);
		li = $('<li></li>');
		li.append($('<label>New: </label><input id="fileupload" type="file" name="image" data-url="/fotos/upload/single/ajax/"/>'));
		ul.append(li);
		return $('<div></div>').append(ul).html();
	}

	function addImageButtonClick(e, data) {
		var editor = data.editor;
		var button = data.button;
		var command = data.command;
		$('#fileupload').fileupload({
			dataType: 'json',
			done: function (e, data) {
				var url = data.result.data.url;
				var $img = $('<div><img src="' + url + '" /></div>');
				editor.execCommand(command, $img.html(), null, button);
				editor.hidePopups();
				editor.focus();
				IMAGES_URLS.push(url);
			}
		});
		$('.wysiwyg_box div').click(function () {
			var src = $(this).find('img').attr('src');
			var $img = $('<div><img src="' + src + '" /></div>');
			editor.execCommand(command, $img.html(), null, button);
			editor.hidePopups();
			editor.focus();
		});
	}

	function load() {
		$(window).load(function () {

		});
	}

})(jQuery);
