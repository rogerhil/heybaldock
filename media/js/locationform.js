$(window).load(function () {
	$('input[name=latitude]').parent().hide();
	$('input[name=longitude]').parent().hide();
	$('input[name=zipcode]').change(getZipcode);
	var $mapCanvas = $("#map_canvas");
	initialize();
	var $country = $('input[name=country]');
	var $li = $("<li>");
	var $ul = $("<ul>");
	var $ulButton = $('<ul id="view_address_map">');
	var $liButton = $("<li>");
	var $button = $('<input type="button" value="View address on map" />');
	$button.click(testFormAddress);
	$li.append($mapCanvas);
	$ul.append($li);
	$ul.insertAfter($country);
	$liButton.append($('<label>'));
	$liButton.append($button);
	$ulButton.append($liButton);
	$ulButton.insertAfter($country);

	var $zip = $('input[name=zipcode]');
	var $street = $('input[name=street]');
	var $number = $('input[name=number]');
	var $district = $('input[name=district]')
	var $city = $('input[name=city]');
	var $state = $('select[name=state]');

	var cleanMap = function () {
		$mapCanvas.slideUp();
		$('input[name=latitude]').val("");
		$('input[name=longitude]').val("");
	};
	$zip.change(cleanMap);
	$street.change(cleanMap);
	$number.change(cleanMap);
	$district.change(cleanMap);
	$city.change(cleanMap);
	$state.change(cleanMap);
	if ($('input[name=latitude]').parent().find('ul.errorlist')) {
		var msg = gettext("You must check over the address on map before submit the form.");
		var $errmsg = $('<ul class="errorlist"><li>' + msg + '</li></ul>');
		$errmsg.css("margin", "10px 0px -5px 0px");
		$errmsg.insertBefore($("#view_address_map"));

	}
});