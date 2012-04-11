/**
 @preserve CLEditor CMS Plugin v0.0.1
 requires CLEditor v1.2.2 or later

 Copyright 2011, Rogerio Hilbert
*/

// ==ClosureCompiler==
// @compilation_level SIMPLE_OPTIMIZATIONS
// @output_file_name jquery.cleditor.cmsplugin.min.js
// ==/ClosureCompiler==

(function($) {

  // Define the table button
  $.cleditor.buttons.cmstags = {
    name: "cmstags",
    image: "table.gif",
    title: "Insert CMS Tag",
    command: "inserthtml",
    popupName: "cmstags",
    popupClass: "cleditorPrompt",
    popupContent: buildPopupContent(),
    buttonClick: cmstagsButtonClick
  };

  // Add the button to the default controls
  $.cleditor.defaultOptions.controls += ' cmstags';

  function buildPopupContent() {
	load();
	var ul = $('<ul></ul>');
	var tag, li;
	if (!window.CMS_TAGS) return;
	for (var k = 0; k < CMS_TAGS.length; k++) {
		tag = CMS_TAGS[k];
		li = $('<li tagname="' + tag[0]  + '">' + tag[1]  + '</li>');
		li.css('list-style', 'none');
    	li.css('padding', '5px');
		li.css('font-size', '12px');
		li.css('cursor', 'pointer');
		li.css('background-image', 'url(/media/img/content_bg_2.png)')
		li.css('margin-bottom', '5px');
		li.css('border-radius', '5px');
		ul.append(li);
	}
	li.css('margin-bottom', '0px');
	return ul.html();
  }

  function cmsblock(tagname, title) {
	  var input = $('<input type="text" disabled="disabled" readonly="readonly" value="' + title + '">');
	  input.attr('class', 'cmstag');
	  input.attr('cmstag', tagname);
	  return $('<div>').append(input).html();
  }

  function cmstagsButtonClick(e, data) {
    $(data.popup).children()
      .unbind("click")
      .bind("click", function(e) {
		var tagname = $(this).attr('tagname');
		var title = $(this).html();
        var editor = data.editor;
		var block = cmsblock(tagname, title);
        if (block)
          editor.execCommand(data.command, block, null, data.button);
        editor.hidePopups();
        editor.focus();
      });

    }

	function load() {
		$(window).load(function () {

			$('textarea').each(function () {
				var reg = /\{% (\w+) %\}/;
				var html = $(this).html();
				var match = html.match(reg);
				var tagname;
				while (match) {
					tagname = match[1];
					html = html.replace(match[0], cmsblock(tagname, tagname));
					match = html.match(reg);
				}
				$(this).html(html);
			});
			$('form').submit(function () {
				$(this).find('textarea').each(function () {
					var cont = $('<div>' + $(this).val() + '</div>');
					cont.find('input.cmstag').each(function () {
						var cmstag = $(this).attr('cmstag');
						$(document.createTextNode('{% ' + cmstag + ' %}')).insertAfter($(this));
						$(this).remove();
					});
					$(this).val(cont.html());
					$(this).html(cont.html());
					$(this).data().cleditor.updateFrame();
				});
				return true;
			});
		});
	}

})(jQuery);
