
$(window).load(function () {
	$("#member_permissions_selector input[name=member]").unbind('click').click(function () {
		$("div.member_permissions").hide();
		$permDiv = $("#member_permissions_" + $(this).val());
		$permDiv.fadeIn();
	});
});