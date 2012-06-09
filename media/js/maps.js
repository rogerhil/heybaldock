var geocoder;
var map;

function initialize() {
    geocoder = new google.maps.Geocoder();
	var $mapCanvas = $("#map_canvas");
	$mapCanvas.parent().parent().find('ul').css("padding", 0);
    var myOptions = {
        zoom: 16,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
	    streetViewControl: true,
		scrollwheel: false
    }
    map = new google.maps.Map($mapCanvas[0], myOptions);
}

function testFormAddress() {
	var $mapCanvas = $("#map_canvas");
	var address = [], addr = '';
	var $ul, success = true;
	$mapCanvas.slideUp();
	address.push($('input[name=street]'));
	address.push($('input[name=number]'));
	address.push($('input[name=district]'));
	address.push($('input[name=city]'));
	address.push($('select[name=state]'));
	address.push($('input[name=country]'));
	for (var k = 0; k < address.length; k++) {
		clearAjaxErrorMessage(address[k]);
		if (!address[k].val()) {
			$ul = ajaxErrorMessage("This field is required");
			$ul.insertBefore(address[k]);
			success = false;
		} else {
			addr += ' ' + address[k].val();
		}
	}
	if (success) {
		codeAddress(addr);
	}
}

function codeAddress(address) {
	var $mapCanvas = $("#map_canvas");
	fullHeight();
	contentHeightAuto();
	$mapCanvas.slideDown(300, function () {
		google.maps.event.trigger(map, 'resize'); // Important to fix the map of hidden element
		fullHeight();
	});
    geocoder.geocode({'address': address}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			var location = results[0].geometry.location;
			map.setCenter(location);
			var marker = new google.maps.Marker({
				map: map,
				position: location
			});
			$('input[name=latitude]').val(location.lat());
			$('input[name=longitude]').val(location.lng());
			contentHeightAuto();
		} else {
			alert("Geocode error: " + status);
		}
    });
}

function codeLatLng(lat, lng) {
	var $mapCanvas = $("#map_canvas");
	fullHeight();
	contentHeightAuto();
	$mapCanvas.slideDown(300, function () {
		google.maps.event.trigger(map, 'resize'); // Important to fix the map of hidden element
		fullHeight();
	});
	var latlng = new google.maps.LatLng(lat, lng);
    map.setCenter(latlng);
 	var marker = new google.maps.Marker({
		map: map,
		position: latlng
    });
}

function ajaxErrorMessage(msg) {
	var $ul = $('<div><ul class="errorlist ajaxerror"><li>' + msg + '</li></ul></div>');
	return $ul;
}

function clearAjaxErrorMessage($input) {
	$input.parent().find('ul.ajaxerror').remove();
}

function getZipcode() {
	var url = '/eventos/locais/address_by_zipcode/ajax/';
	var $zip = $('input[name=zipcode]');
	var zip = $zip.val();
	var $street = $('input[name=street]');
	var $district = $('input[name=district]')
	var $city = $('input[name=city]');
	var $state = $('select[name=state]');
	var addressList = [$street, $district, $city, $state];
	var pos = {left: 20, top: 5};
	for (var k = 0; k < addressList.length; k++) {
		addressList[k].attr("disabled", "disabled");
		addressList[k].val("         Searching the address by zip code...");
		showLoadingIconNearTo(addressList[k], pos);
	}

	$.ajax({
		'type': 'get',
		'url': url,
		'data': {zipcode: zip},
		'dataType': 'json',
		'success': function (data) {
			if (data.data) {
				data = data.data;
				dropAllLoadingIcons();
				$(addressList).each(function () {
					$(this).val("")
					$(this).removeAttr("disabled");
				});
				if (data.street || data.district || data.city || data.state) {
					$(addressList).each(function () {
						$(this).hide();
						$(this).fadeIn(1000);
					});
					$street.val(data.street);
					$district.val(data.district);
					$city.val(data.city);
					$state.val(data.state);
				} else {
					var color = $zip.css("color");
					$zip.val(zip + " is an invalid zipcode, please check over again.");
					$zip.css("color", "red");
					$zip.attr("disabled", "disabled");
					window.setTimeout(function () {
						$zip.fadeOut(1000, function () {
							$zip.val(zip);
							$zip.css("color", color);
							$zip.fadeIn(200, function () {
								$zip.removeAttr("disabled");
								$zip.select();
								$zip.focus();
							});
						});
					}, 2000);
				}
			} else {
				console.log(data);
			}
		}
	});
}