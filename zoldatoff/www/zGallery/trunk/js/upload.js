/**
 * @author dsoldatov
 */

var dProgress = 0;
var progress = 0;

$(document).ready( function() {
	$('#topDiv').hide();
	//$.getJSON('php/upload.php', {object: 'newimages'}, listNewImages);
	//$.getJSON('php/upload.php', {object: 'images', album_id: 1}, listImages);
	//$.getJSON('php/upload.php', {object: 'albums', category_id: 0}, listAlbums);
	$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
})

function listNewImages(jsonData) {
	progress = dProgress = 0;
	list(jsonData, 'newimages');
}

function listImages(jsonData) {
	list(jsonData, 'images');	
}

function listAlbums(jsonData) {
	list(jsonData, 'albums');	
}

function listCategories(jsonData) {
	list(jsonData, 'categories');	
}

function list(jsonData, object) {
	var nObjects 
	switch (object) {
		case 'newimages':
			nObjects = jsonData.objectlist.length;
			$('#imageThumbsUL').empty();
			break;
		case 'images':
			nObjects = jsonData.objectlist.image_list.length;
			$('#imageThumbsUL').empty();
			break;
		case 'albums':
			nObjects = jsonData.objectlist.album_list.length;
			$('#albumThumbsUL').empty();
			break;
		case 'categories':
			nObjects = jsonData.objectlist.category_list.length;
			$('#categoryThumbsUL').empty();
			break;
	}		
	
	for (var i=0; i<nObjects; i++){
		switch (object) {
			case 'newimages':
				$('#imageThumbsUL').append('<li><img id="img' + i + '" class="iThumbs" src="css/loader.gif"/> </li>');
				//$('#img'+i).attr('myID', i);
				break;
			case 'images':
				$('#imageThumbsUL').append('<li><img id="img' + i + '" class="iThumbs" src="' + jsonData.objectlist.image_list[i].thumb_src + '"/> </li>');
				$('#img'+i).attr('myID', jsonData.objectlist.image_list[i].image_id);
				break;
			case 'albums':
				$('#albumThumbsUL').append('<li><img id="alb' + i + '" class="aThumbs" src="' + jsonData.objectlist.album_list[i].image.thumb_src + '"/> </li>');
				$('#alb'+i).attr('myID', jsonData.objectlist.album_list[i].album_id);
				break;
			case 'categories':
				$('#categoryThumbsUL').append('<li><img id="cat' + i + '" class="cThumbs" src="' + jsonData.objectlist.category_list[i].image.thumb_src + '"/> </li>');
				$('#cat'+i).attr('myID', jsonData.objectlist.category_list[i].category_id);
				break;
		}
	}
	
	$('.iThumbs').load( function(){
		$(this).center();
	});
	
	$('.aThumbs').load( function(){
		$(this).center();
	});
	
	$('.cThumbs').load( function(){
		$(this).center();
	});
	
	switch (object) {
		case 'newimages':
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
			break;
			
		case 'images':
			$('.iThumbs').click( function(){
				$(this).parent().addClass('active');
			})
			break;
			
		case 'albums':
			$('.aThumbs').click( function(){
				$('.aThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'images', album_id: $(this).attr('myID')}, listImages)
			})
			$('#alb0').click();
			break;
			
		case 'categories':
			$('.cThumbs').click( function(){
				$('.cThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'albums', category_id: $(this).attr('myID')}, listAlbums);
			})
			$('#cat0').click();
			break;
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
 
