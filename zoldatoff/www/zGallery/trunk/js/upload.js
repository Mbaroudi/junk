/**
 * @author dsoldatov
 */

var dProgress;
var progress;

var mode = 'move';
/* Режим работы:
 * new (? -> manage)
 * copy
 * move
 * manage
 */


$(document).ready( function() {
	//
	switch (mode) {
		case 'copy':
		case 'move':
		case 'manage':
			$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
			break;
		case 'new':
			$.getJSON('php/upload.php', {object: 'newimages'}, listNewImages);
			break;
	}
})

// Вывести список загруженных в папку upload изображений
function listNewImages(jsonData) {
	progress = dProgress = 0;
	list(jsonData, 'newimages');
}

//Вывести список изображений из альбома
function listImages(jsonData) {
	list(jsonData, 'images');	
}

//Вывести список альбомов из категории
function listAlbums(jsonData) {
	list(jsonData, 'albums');	
}

//Вывести список категорий
function listCategories(jsonData) {
	list(jsonData, 'categories');	
}

//Вывод списка объектов типа object
function list(jsonData, object) {
	var nObjects;
	
	// Очищаем соответствующий список
	switch (object) {
		case 'newimages':
			nObjects = jsonData.objectlist.length;
			$('#imageThumbsUL').empty();
			break;
		case 'images':
			nObjects = jsonData.objectlist.image_list.length;
			$('#imageThumbsUL').empty();
			$('#iCaption').html('Images from album "' + jsonData.objectlist.name + '"');
			break;
		case 'albums':
			nObjects = jsonData.objectlist.album_list.length;
			$('#albumThumbsUL').empty();
			$('#aCaption').html('Albums from category "' + jsonData.objectlist.name + '"');
			break;
		case 'categories':
			nObjects = jsonData.objectlist.category_list.length;
			$('#categoryThumbsUL').empty();
			break;
	}		
	
	//Заполняем соответствующий список
	for (var i=0; i<nObjects; i++){
		switch (object) {
			case 'newimages':
				$('#imageThumbsUL').append('<li><img id="img' + i + '" class="iThumbs" src="css/loader.gif"/> </li>');
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
	
	//Позиционируем изображения
	$('li img').load( function(){
		$(this).center();
	});
	

	/* Здесь нужно применять разную логику для разных режимов работы:
	 * manage new images
	 * copy images/albums
	 * move images/albums
	 * create/edit albums/categories/images
	 * 
	 * idea: invisible category
	 */
	switch (object) {
		case 'newimages':
			// Выводим поверх всего DIV с probressbar-ом
			dProgress = 100 / nObjects;
			$('#topDiv').show();
			$("#progressbar").progressbar({value: 0});
			
			// Для каждого файла запускаем процедуру импорта в галерею
			for (var i = 0; i < nObjects; i++) 
				$.getJSON('php/upload.php', {filename: jsonData.objectlist[i].filename,	number: i}, getUploadStatus);
			
			break;
			
		case 'images':
			// Изображения можно выделять
			$('.iThumbs').click( function(){
				$(this).parent().toggleClass('active');
			});
			
			// Изображения можно перетаскивать внутри группы images2albums
			$('.iThumbs').make_draggable('images2albums');
			
			break;
			
		case 'albums':
			// При выделении альбома подгружаются изображения из него
			$('.aThumbs').click( function(){
				$('.aThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'images', album_id: $(this).attr('myID')}, listImages);
			})
			
			// Выделяем первый альбом
			//$('#alb0').click();
			
			// На альбомы можно перетаскивать изображения
			$(".aThumbs").make_droppable('images2albums');
			
			// Альбомы можно перетаскивать внутри группы albums2categories
			$('.aThumbs').make_draggable('albums2categories');
			
			break;
			
		case 'categories':
			// При выделении категории подгружаются ее альбомы
			$('.cThumbs').click( function(){
				$('.cThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'albums', category_id: $(this).attr('myID')}, listAlbums);
			})
									
			// На категории можно перетаскивать альбомы
			$(".cThumbs").make_droppable('albums2categories');
			
			// Выделяем первую категорию
			//$('#cat0').click();
			break;
	}
}

jQuery.fn.make_droppable = function(scope) {
	$(this).droppable({
		drop: function(event, ui) {
			dropObjectID = $(this).attr('myID');
			
			// Перебираем drag'n'drop-нутые альбомы и перемещаем их в новую категорию
			// idea: сейчас альбом удаляется изо всех категорий. Нужно действовать мягче...
			$('#draggingContainer').children().each(function() {
				$('#' + $(this).attr('id')).parent().removeClass('active');
				dragObjectID = $(this).attr('myID');						
				
				switch (scope) {
					case 'images2albums':     
						$.getJSON('php/upload.php', {action: mode + scope, imageid: dragObjectID, albumid: dropObjectID}, displayImageAction);
						break;
					case 'albums2categories': 
						$.getJSON('php/upload.php', {action: mode + scope, albumid: dragObjectID, categoryid: dropObjectID}, displayAlbumAction);
						break;
				}
			});
		},
		hoverClass: 'drophover',
		scope: scope,
		tolerance: 'pointer'
	});
}

jQuery.fn.make_draggable = function(scope) {
	$(this).draggable({
		appendTo: 'body',
		containment: '#containerDiv',
		helper: function(){
			// Собираем выделенные альбомы в div и тащим...
			switch (scope) {
				case 'images2albums':     
					var selected = $('#imageThumbsUL .active img');
					break;
				case 'albums2categories': 
					var selected = $('#albumThumbsUL .active img');
					break;
			}
			
			if (selected.length === 0) {
				selected = $(this);
			}
			var container = $('<div/>').attr('id', 'draggingContainer');
			container.append(selected.clone());
			return container; 
		},
		opacity: 0.5,
		revert: 'invalid',
		scope: scope
	});
}

// Выводим изображение обработанного файла и сообщаем об этом
function getUploadStatus(jsonData) {
	$('#img' + jsonData.result.number).attr('src', jsonData.result.filename);
	
	$.gritter.add({
		title: 'Image imported in gallery',
		text: jsonData.result.filename,
		image: jsonData.result.filename,
		sticky: false, 
		time: 8000
	});
	
	progress += dProgress;
	
	$("#progressbar").progressbar('option', 'value', progress);
	if (progress > 99) {
		$('#topDiv').hide();
		mode = 'move';
		$('#alb0').click();
	}
}

// Убираем изображение перемещенного файла и сообщаем об этом
function displayImageAction(jsonData) {
	$('.iThumbs').each(function(){
		if ($(this).attr('myID') == jsonData.result.image_id) $(this).parent().empty(); 
	});
	
	$.gritter.add({
		title: 'Image successfully copied/moved:',
		text: jsonData.result.name,
		image: jsonData.result.thumb_src,
		sticky: false, 
		time: 8000
	});
}

function displayAlbumAction(jsonData) {
	$('.aThumbs').each(function(){
		if ($(this).attr('myID') == jsonData.result.album_id) $(this).parent().empty(); 
	});
	
	$.gritter.add({
		title: 'Album successfully copied/moved:',
		text: jsonData.result.name,
		image: jsonData.result.image.thumb_src,
		sticky: false, 
		time: 8000
	});
}
 
