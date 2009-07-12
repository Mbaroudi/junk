/**
 * @author dsoldatov
 */

$(document).ready( function() {
	$.getJSON('php/upload.php', {}, getList);
})

function getList(jsonData) {
	nFiles = jsonData.file_list.length;
	
	var myHTML = '';
	
	for (var i=0; i<nFiles; i++){
		myHTML += '<li>';
		myHTML += '<img id="img' + i + '" src="css/loader.gif"/>';
		myHTML += '</li>';
	}
	$('#thumbs').append(myHTML);

	for (var i = 0; i < nFiles; i++) {
		$.getJSON('php/upload.php', {filename: jsonData.file_list[i].filename, number: i}, getStatus);
	}
}

function getStatus(jsonData) {
	$('#img' + jsonData.result.number).attr('src', jsonData.result.filename);
}
 
