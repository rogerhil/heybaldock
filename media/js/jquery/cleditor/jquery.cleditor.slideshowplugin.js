/**
 @preserve CLEditor CMS Plugin v0.0.1
 requires CLEditor v1.2.2 or later

 Copyright 2011, Rogerio Hilbert
*/

// ==ClosureCompiler==
// @compilation_level SIMPLE_OPTIMIZATIONS
// @output_file_name jquery.cleditor.slideshowplugin.min.js
// ==/ClosureCompiler==

(function($) {

	// Define the table button
	$.cleditor.buttons.slideshow = {
		name: "slideshow",
		image: "slideshow.png",
		title: "Insert Slide Show",
		command: "inserthtml",
		popupName: "slideshow",
		popupClass: "cleditorPrompt",
		popupContent: buildPopupContent(),
		buttonClick: slideShowButtonClick
	};

	// Add the button to the default controls
	$.cleditor.defaultOptions.controls += 'slideshow';

	function buildPopupContent() {
		var $model = $("#slide_show_menu_box");
		var html = $model.html();
		$model.remove();
		return html;
	}

	function appendImageItem(url, value, link) {
		var $img = $('<img src="' + url + '" />');
		var $item = $('<div class="item"></div>');
		value = value || '';
		link = link || '';
		$item.append($('<a href="javascript:;" class="remove_slideshow_item">Remove</a><br/>'));
		$item.append($img);
		$item.append($('<br/><input name="description" value="' + value + '" />'));
		$item.append($('<br/><input name="link" value="' + link + '" />'));
		$('.slide_show_menu .selected_images').append($item);
		$('.slide_show_menu .selected_images a.remove_slideshow_item').unbind('click').click(function (e) {
			e.stopPropagation();
			$(this).parent().remove();
		});
	}

	function slideShowButtonClick(e, data) {
		$('.slide_show_menu .selected_images').html('');
		var editor = data.editor;
		var button = data.button;
		var command = data.command;
		$('#slideshow_fileupload').fileupload({
			dataType: 'json',
			done: function (e, data) {
				var url = data.result.data.url;
				var $img = $('<img src="' + url + '" />');
				var $item = $('<div class="item"></div>');
				$item.append($img);
				appendImageItem(url);
				$('.slide_show_menu .image_selector').append($item);
			}
		});
		$('.slide_show_menu .image_selector div.item').click(function () {
			appendImageItem($(this).find('img').attr('src'));
		});

		$('.slide_show_menu input[name=slideshow_submit]').click(function () {
			var el = newSlideShow();
			if (!el) {
				return;
			}
			var html = $('<div></div>').append(el).html();
			editor.execCommand(command, html, null, button);
			editor.hidePopups();
			editor.focus();
			initSlideShow();
		});

		$('.slide_show_menu input[name=slideshow_edit_submit]').click(function () {
			$($('#content iframe')[0].contentDocument.documentElement).find('div.slideshow').remove();
			var html = $('<div></div>').append(newSlideShow()).html();
			editor.execCommand(command, html, null, button);
			editor.hidePopups();
			editor.focus();
			initSlideShow();
		});
	}

	function newSlideShow() {
		if (!$('.slide_show_menu .selected_images div.item').length) {
			alert('You must select at least one image to the SlideShow');
			return;
		}
		var $div = $('<div class="slideshow"></div>');
		var $figure, $img, description, $a, link;
		var width = $('.slide_show_menu input[name=slideshow_width]').val();
		var height = $('.slide_show_menu input[name=slideshow_height]').val();
		var time = $('.slide_show_menu input[name=slideshow_time]').val();
		if (!width) {
			alert('Width is required');
			return;
		}
		if (!height) {
			alert('Height is required');
			return;
		}
		if (!time) {
			alert('Time is required');
			return;
		}
		$('.slide_show_menu .selected_images div.item').each(function () {
			$img = $(this).find('img');
			description = $(this).find('input[name=description]').val();
			link = $(this).find('input[name=link]').val() || '#';
			$figure = $('<figure class="slide"></figure>');
			$img.css('height', height + 'px');
			$img.css('width', width + 'px');
			$a = $('<a href="' +  link + '"></a>');
			$a.append($img);
			$figure.append($a);
			$figure.append($('<div class="slideshow_description">' + description + '</div>'));
			$div.append($figure);
		});
		$div.css('width', Number(width) + 10 + 'px');
		$div.css('height', Number(height) + 10 + 'px');
		$div.attr('time', time);
		window.setTimeout(function () {
			initWysiwygSlideshow();
		}, 1500);
		return $div;
	}

	function initWysiwygSlideshow() {
		var ib = $('div.cleditorButton[title="Insert Slide Show"]');
		$($('#content iframe')[0].contentDocument.documentElement).find('div.slideshow').each(function () {
			$(this).prepend($('<a href="javascritpt:;" class="slideshow_edit">EDIT THIS SLIDESHOW</a>'))
		});

		$($('#content iframe')[0].contentDocument.documentElement).find('a.slideshow_edit').click(function (e) {
			e.stopPropagation();
			ib.trigger('click');
			var $ss = $(this).parent();
			var $imgs = $ss.find('figure');
			var width, height;
			var time = $ss.attr('time');
			window.setTimeout(function () {
				$('input[name=slideshow_submit]').hide();
				$('input[name=slideshow_edit_submit]').show();
				$imgs.each(function () {
					var $img = $(this).find('img');
					var url = $img.attr('src');
					var description = $(this).find('div.slideshow_description').html();
					var link = $(this).find('a').attr('href');
					appendImageItem(url, description, link);
					width = $img.css('width').replace('px', '');
					height = $img.css('height').replace('px', '');
					$('.slide_show_menu input[name=slideshow_width]').val(width);
					$('.slide_show_menu input[name=slideshow_height]').val(height);
					$('.slide_show_menu input[name=slideshow_time]').val(time);
				});
			}, 500);
		});
	}

	window.setTimeout(function () {
		initWysiwygSlideshow();
	}, 1500);

	$('form').submit(function () {
		$(this).find('textarea').each(function () {
			var cont = $('<div>' + $(this).val() + '</div>');
			cont.find('a.slideshow_edit').remove();
			$(this).val(cont.html());
			$(this).html(cont.html());
			$(this).data().cleditor.updateFrame();
		});
		return true;
	});

})(jQuery);
