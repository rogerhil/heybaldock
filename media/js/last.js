function startCursor() {
	$('body').append('<img style="position:absolute;cursor:none;" id="mycursor" src="/media/img/loading_24.png" />');
	var element = $('body');
	element.css('cursor','none');
	$(element).mousemove(function(e){
		$('#mycursor').css('left', e.clientX - 10).css('top', e.clientY + 250);
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
});

ajax = function (options) {
	$("div.pp_overlay").show();
	var suc = options.success;
	options.success = function (data) {
		$("div.pp_overlay").hide();
		suc(data);
	}
	$.ajax(options);
}

