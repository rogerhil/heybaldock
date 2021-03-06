$(window).load(function () {
	//formFieldsWidth();
	$("div.menu_item").mouseover(function () {
		//$(this).animate({"box-shadow": "#e9892c 0px -=5px"}, "slow");
	});
	$("#search input").placeholder('Search...');
	animateImages();
	loadManagementMenu();
});

$(window).bind('hashchange', function() {

});

function fullHeight() {
	if (IS_MAIN_PAGE) return;
	contentHeightAuto();
	var $content = $("#content");
	var $emptyPortlet = $("#empty_portlet");
	var $footer = $("#footer");
	if ($emptyPortlet.length && $footer.length) {
		var ediff = $footer.position().top - $emptyPortlet.position().top - 30;
		$emptyPortlet.css("height", ediff + 'px');
	}
	if ($footer.length) {
		var cdiff = $footer.position().top - $content.position().top - 30;
		$content.css("min-height", cdiff + 'px');
	}
	contentHeightAuto();
}

function contentHeightAuto() {
	if (IS_MAIN_PAGE) return;
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

function showLoadingIconNearTo($obj, position) {
	var $loading = $('<div class="loading_icon"><img src="/media/img/loading_24.png" /></div>');
	var pos = $obj.position();
	for (var k in position) {
		$loading.css(k, (pos[k] + position[k]) + "px");
	}
	$('body').append($loading);
}

function dropAllLoadingIcons() {
	$('div.loading_icon').remove();
}

function closeSimpleMenus() {
	$('.simple_menu').slideUp();
}

function loadManagementMenu() {
	$("#management_menu .menu_button").click(function () {
		var $menu = $("#management_menu .content_menu");
		if ($menu.is(':hidden')) {
			$menu.slideDown();
		} else {
			$menu.slideUp();
		}
	});
	$("#management_menu .content_menu").mouseleave(function () {
		$(this).slideUp();
	});
}