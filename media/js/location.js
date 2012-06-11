
function deleteLocation() {
	var conf = window.confirm("Are you sure you want to delete this Location? WARNING: ALL RELATED EVENTS WILL BE LOST!!! The only way to rescue back will be through drafts.");
	if (conf) {
		document.forms.delete_action.submit();
	}
}