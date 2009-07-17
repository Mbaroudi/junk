/**
 * @author dsoldatov
 */

var dProgress = 0;
var progress = 0;

$(document).ready( function() {
	$.getJSON('php/upload.php', {object: 'newimages'}, listNewImages);
	$.getJSON('php/upload.php', {object: 'albums'}, listAlbums);
	$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
})

function listNewImages(jsonData) {
	progress = dProgress = 0;
	list(jsonData, 'newimages');
}

function listAlbums(jsonData) {
	list(jsonData, 'albums');	
}

function listCategories(jsonData) {
	list(jsonData, 'categories');	
}

function list(jsonData, object) {
	var nObjects = jsonData.objectlist.length;
	
	var myHTML = '';
	for (var i=0; i<nObjects; i++){
		myHTML += '<li>';
		myHTML += '<img id="img' + i + '" class="cThumbs" src="';
		switch (object) {
			case 'newimages':
				myHTML += 'css/loader.gif'
				break;
			case 'albums':
				myHTML += jsonData.objectlist[i].image_src;
				break;
			case 'categories':
				myHTML += jsonData.objectlist[i].image_src;
				break;
		}
		myHTML += '"/> </li>';
	}
	
	switch (object) {
		case 'newimages':
			$('#imageThumbsUL').append(myHTML);
			break;
		case 'albums':
			$('#albumThumbsUL').append(myHTML);
			break;
		case 'categories':
			$('#categoryThumbsUL').append(myHTML);
			break;
	}
	
	$('.cThumbs').load( function(){
		$(this).center();
	});
	
	if (object == 'newimages') {
		dProgress = 100 / nObjects;
		
		$('#topDiv').show();
		
		$("#progressbar").progressbar({
			value: 0
		});
		
		for (var i = 0; i < nObjects; i++) {
			$.getJSON('php/upload.php', {
				filename: jsonData.objectlist[i].filename,
				number: i
			}, getUploadStatus);
		}
	}
}

function getUploadStatus(jsonData) {
	$('#img' + jsonData.result.number).attr('src', jsonData.result.filename);
	
	$.gritter.add({
		title: 'Image processed',
		text: jsonData.result.filename,
		image: jsonData.result.filename,
		sticky: false, 
		time: 8000
	});
	
	progress += dProgress;
	
	$("#progressbar").progressbar('option', 'value', progress);
	if (progress > 95) $('#topDiv').hide();
}
 
