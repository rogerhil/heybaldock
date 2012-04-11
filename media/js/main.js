$(window).load(function () {
	//formFieldsWidth();
	$("div.menu_item").mouseover(function () {
		$(this).fadeOut(1);
		$(this).fadeIn();


	});
	animateImages();
});

$(window).bind('hashchange', function() {

});

function fullHeight() {
	contentHeightAuto();
	var $content = $("#content");
	var $emptyPortlet = $("#empty_portlet");
	var $footer = $("#footer");
	var cdiff = $footer.position().top - $content.position().top - 30;
	var ediff = $footer.position().top - $emptyPortlet.position().top - 30;
	$content.css("height", cdiff + 'px');
	$emptyPortlet.css("height", ediff + 'px');
}

function contentHeightAuto() {
	$content = $("#content");
	$content.css('height', 'auto');
}

function formFieldsWidth() {
	$("form[name=draft_form] input").each(function () {
		var $this = $(this);
		var length = $this.attr('maxlength');
		if (length < 150) {
			$this.css('width', 20 + length*3 + 'px');
		}
	});
}
	
function animateImages() {
	$('.top_images img').each(function () {
		$(this).mouseover(function () {
			$(this).animate({"right": "+=" + 20 + "px"}, "fast");
			$(this).animate({"right": "-=" + 40 + "px"}, "fast");
			$(this).animate({"right": "+=" + 20 + "px"}, "fast");
			//$(this).effect("shake", { times:1 }, 200);
		});
	});

	$('.top_images img.hand').mouseover(function () {
		
		$(this).circulate({
			 speed: 800,                  // Speed of each quarter segment of animation, 1000 = 1 second
			 height: -900,                 // Distance vertically to travel
			 width: 80,                  // Distance horizontally to travel
			 sizeAdjustment: 80,         // Percentage to grow or shrink
			 loop: false,                 // Circulate continuously
			 zIndexValues: [2, 2, -2, -2]   // Sets z-index value at each stop of animation
		});


		//$(this).flip({
		//	direction:'tb'
		//})
	});
}


