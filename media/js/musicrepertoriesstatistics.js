$(window).load(function () {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");

	loadRepertory();

	loadGlobalCancelActions();

});

function loadRepertory() {
	var $repertory_content = $("#repertory_content");
	var repertory_id = $repertory_content.attr("repertory_id");
	loadRatings($("td.ratings_cel"));
	loadAudio();
	$repertory_content.find('img.player').click(changePlayerButton);
	calculateTimeTotal();
	initSortTable();
}