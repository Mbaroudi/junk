/**
 * @author dsoldatov
 */

var dProgress;
var progress;

$(document).ready( function() {
	//$.getJSON('php/upload.php', {object: 'newimages'}, listNewImages);
	$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
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

//Вывести список akm,jvjd из категории
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
	
	//Заполняем соответствующий список
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
	
	//Позиционируем изображения
	$('.iThumbs').load( function(){
		$(this).center();
	});
	
	$('.aThumbs').load( function(){
		$(this).center();
	});
	
	$('.cThumbs').load( function(){
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
			$("#progressbar").progressbar({
				value: 0
			});
			
			// Для каждого файла запускаем процедуру импорта в галерею
			for (var i = 0; i < nObjects; i++) {
				$.getJSON('php/upload.php', {
					filename: jsonData.objectlist[i].filename,
					number: i
				}, getUploadStatus);
			}
			
			break;
			
		case 'images':
			// Изображения можно выделять
			$('.iThumbs').click( function(){
				$(this).parent().toggleClass('active');
			});
			
			// Изображения можно перетаскивать внутри группы images2albums
			$('.iThumbs').draggable({
				appendTo: 'body',
				containment: '#containerDiv',
				helper: function(){
					// Собираем выделенные изображения в div и тащим...
					var selected = $('#imageThumbsUL .active img');
					if (selected.length === 0) {
						selected = $(this);
					}
					var container = $('<div/>').attr('id', 'draggingContainer');
					container.append(selected.clone());
					return container; 
				},
				opacity: 0.5,
				revert: 'invalid',
				scope: 'images2albums'
			});
			
			break;
			
		case 'albums':
			// При выделении альбома подгружаются изображения из него
			$('.aThumbs').click( function(){
				$('.aThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'images', album_id: $(this).attr('myID')}, listImages)
			})
			
			// Выделяем первый альбом
			$('#alb0').click();
			
			// На альбомы можно перетаскивать изображения
			$(".aThumbs").droppable({
				drop: function(event, ui) {
					albumID = $(this).attr('myID');
					
					// Перебираем drag'n'drop-нутые изображения и перемещаем их в новый альбом
					// idea: сейчас изображение удаляется изо всех альбомов. Нужно действовать мягче...
					$('#draggingContainer').children().each(function() {
						$('#' + $(this).attr('id')).parent().removeClass('active');
						imageID = $(this).attr('myID');						
						$.getJSON('php/upload.php', {action: 'moveimages2albums', imageid: imageID, albumid: albumID}, displayImageMoved);
					});
				},
				hoverClass: 'drophover',
				scope: 'images2albums',
				tolerance: 'pointer'
			});
			break;
			
		case 'categories':
			// При выделении категории подгружаются ее альбомы
			$('.cThumbs').click( function(){
				$('.cThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'albums', category_id: $(this).attr('myID')}, listAlbums);
			})
			
			// Выделяем первую категорию
			$('#cat0').click();
			break;
	}
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
	if (progress > 95) $('#topDiv').hide();
}

// Убираем изображение перемещенного файла и сообщаем об этом
function displayImageMoved(jsonData) {
	$('.iThumbs').each(function(){
		if ($(this).attr('myID') == jsonData.result.image_id) $(this).parent().empty(); 
	});
	
	$.gritter.add({
		title: 'Image successfully moved:',
		text: jsonData.result.name,
		image: jsonData.result.thumb_src,
		sticky: false, 
		time: 8000
	});
}
 
