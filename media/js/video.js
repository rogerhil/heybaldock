
function deleteVideoAlbum() {
	var conf = window.confirm("Are you sure you want to delete this Video Album? WARNING: ALL RELATED VIDEOS WILL BE LOST!!! the only way to rescue back will be through drafts.");
	if (conf) {
		document.forms.delete_action.submit();
	}
}