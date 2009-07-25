/**
 * @author dsoldatov
 */

var dProgress;
var progress;

var mode = 'move';
/* Режим работы:
 * new
 * copy
 * move
 * edit
 */

var currentObject;


$(document).ready( function() {
	
	// Disable right click
  	$(document).bind("contextmenu",function(e){
    	return false;
  	});
	
	// Init progressbar
	$("#progressbar").progressbar({value: 0});
	
	// Init edit dialog
	$('#editForm').dialog({
		autoOpen: false,
		modal: true,
		width: 320,
		buttons: {
			'OK': function() {
				var bValid = true;
				$('#title').removeClass('ui-state-error');
				$('#description').removeClass('ui-state-error');

				bValid = bValid && checkLength($('#title'));
				bValid = bValid && checkLength($('#description'));
				
				if (mode == 'copy' || mode == 'move') {
					myJson = $(this).data('json');
					
					switch ($(this).data('object')) {
						case 'images':
							myAction = 'updateimage';
							myId = myJson.image_id;
							break;
						case 'albums':
							myAction = 'updatealbum';
							myId = myJson.album_id;
							break;
						case 'categories':
							myAction = 'updatecategory';
							myId = myJson.category_id;
							break;
					}
					
					if (bValid) {
						$.getJSON('php/upload.php', {
							action: myAction,
							id: myId,
							name: $('#title').val(),
							description: $('#description').val()
						}, function(jsonData){
							$('#' + currentObject).data('json', jsonData.result);
							$('#' + currentObject).parent().effect('highlight', {
								color: '#dddddd'
							}, 1000);
						});
						$(this).dialog('close');
					}
				}
				
				if (mode = 'edit') {
					switch ($(this).data('object')) {
						case 'albums':
							myAction = 'newalbum';
							break;
						case 'categories':
							myAction = 'newcategory';
							break;
					}
					
					if (bValid) {
						$.getJSON('php/upload.php', {
							action: myAction,
							name: $('#title').val(),
							description: $('#description').val()
						}, 
						addNewElement
						);
						$(this).dialog('close');
					}
				}
			},
			'Cancel': function() {
				$(this).dialog('close');
			}
		},
		close: function() {
			$('#title').removeClass('ui-state-error');
			$('#description').removeClass('ui-state-error');
			$('#validateTips').text("Plz, fill-in the information below")
		}
	});
	
	// Init modes menu
	$('.mode', '#modesDiv').click( function() {
		$('.mode', '#modesDiv').removeClass('activeMode');
		$(this).addClass('activeMode');
		
		switch ( $(this).attr('id') ) {
			case 'modeNew':
				mode = 'new';
				break;
			case 'modeCopy':
				mode = 'copy';
				break;
			case 'modeMove':
				mode = 'move';
				break;
			case 'modeEdit':
				mode = 'edit';
				break;
		}
		
		runMode();		
	});
	
	// Run Move mode
	$('#modeMove').click();
	
	// Init scroll interfaces
	$('#iUp').click(function(){
		$('#imageThumbsUL').scrollThumbs(1);
	});
	$('#iDown').click(function(){
		$('#imageThumbsUL').scrollThumbs(-1);
	});
	
	$('#aUp').click(function(){
		$('#albumThumbsUL').scrollThumbs(1);
	});
	$('#aDown').click(function(){
		$('#albumThumbsUL').scrollThumbs(-1);
	});
	
	$('#cUp').click(function(){
		$('#categoryThumbsUL').scrollThumbs(1);
	});
	$('#cDown').click(function(){
		$('#categoryThumbsUL').scrollThumbs(-1);
	});
	
	// Init remove interfaces
	$('#iRemove').click(function(){
		$('#imageThumbsUL').removeElement();
	});
	$('#aRemove').click(function(){
		$('#albumThumbsUL').removeElement();
	});
	$('#cRemove').click(function(){
		$('#categoryThumbsUL').removeElement();
	});
	
	// Init add interfaces
	$('#modeNew').click(function(){
		mode = 'new';
		runMode();
	});
	$('#aAdd').click(function(){
		$('#albumThumbsUL').addElement();
	});
	$('#cAdd').click(function(){
		$('#categoryThumbsUL').addElement();
	});
})

function checkLength(element) {
	if ( element.val().length == 0 ) {
		element.addClass('ui-state-error');
		$('#validateTips').text("Field must not be empty!").effect("highlight",{},1500);
		return false;
	} else {
		return true;
	}
}

function addNewElement(jsonData) {
	if (jsonData.result.album_id) {
		N = $('#albumThumbsUL').children().length + 1;
		$('#albumThumbsUL').append('<li><img id="alb' + N + '" class="aThumbs" src="' + jsonData.result.image.thumb_src + '"/> </li>');
		$('#alb'+N).attr('myID', jsonData.result.album_id);
		$('#alb'+N).data('json', jsonData.result);
	}
	
	if (jsonData.result.category_id) {
		N = $('#categoryThumbsUL').children().length + 1;
		$('#categoryThumbsUL').append('<li><img id="cat' + N + '" class="cThumbs" src="' + jsonData.result.image.thumb_src + '"/> </li>');
		$('#cat'+N).attr('myID', jsonData.result.category_id);
		$('#cat'+N).data('json', jsonData.result);
	}
	
	$('#cat0').click();
}

// Init mode and fetch data
function runMode() {
	switch (mode) {
		case 'copy':
		case 'move':
			$('#iRemove').hide();
			$('#aRemove').hide();
			$('#cRemove').hide();
			$('#aAdd').hide();
			$('#cAdd').hide();
			$('#modeNew').hide();
			$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
			break;
		case 'edit':
			$('#iRemove').show();
			$('#aRemove').show();
			$('#cRemove').show();
			$('#aAdd').show();
			$('#cAdd').show();
			$('#modeNew').show();
			$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
			break;
		case 'new':
			$.getJSON('php/upload.php', {object: 'newimages'}, listNewImages);
			break;
	}
}

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
			$('#albumThumbsUL').empty();
			$('#categoryThumbsUL').empty();
			break;
		case 'images':
			if (jsonData.objectlist.image_list) {
				nObjects = jsonData.objectlist.image_list.length;
			}
			else {
				nObjects = 0;
			}
			$('#imageThumbsUL').empty();
			$('#iCaption').html('Images from album "' + jsonData.objectlist.name + '"');
			break;
		case 'albums':
			if (jsonData.objectlist.album_list) {
				nObjects = jsonData.objectlist.album_list.length;
			}
			else {
				nObjects = 0;
			}
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
				$('#img'+i).data('json', jsonData.objectlist.image_list[i]);
				break;
			case 'albums':
				$('#albumThumbsUL').append('<li><img id="alb' + i + '" class="aThumbs" src="' + jsonData.objectlist.album_list[i].image.thumb_src + '"/> </li>');
				$('#alb'+i).attr('myID', jsonData.objectlist.album_list[i].album_id);
				$('#alb'+i).data('json', jsonData.objectlist.album_list[i]);
				break;
			case 'categories':
				$('#categoryThumbsUL').append('<li><img id="cat' + i + '" class="cThumbs" src="' + jsonData.objectlist.category_list[i].image.thumb_src + '"/> </li>');
				$('#cat'+i).attr('myID', jsonData.objectlist.category_list[i].category_id);
				$('#cat'+i).data('json', jsonData.objectlist.category_list[i]);
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
			$("#progressbar").progressbar('option', 'value', 0);
			
			// Для каждого файла запускаем процедуру импорта в галерею
			for (var i = 0; i < nObjects; i++) 
				$.getJSON('php/upload.php', {filename: jsonData.objectlist[i].filename,	number: i}, getUploadStatus);
			
			break;
			
		case 'images':
			// Изображения можно выделять
			$('.iThumbs').click( function(){
				if (mode == 'edit') $('.iThumbs').parent().removeClass('active');
				$(this).parent().toggleClass('active');
			});
			
			$('.iThumbs').dblclick( function(){
				$(this).editMe(object, $(this).data('json'));
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
			
			$('.aThumbs').dblclick( function(){
				$(this).editMe(object, $(this).data('json'));
			});
			
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
			
			$('.cThumbs').dblclick( function(){
				$(this).editMe(object, $(this).data('json'));
			});
									
			// На категории можно перетаскивать альбомы
			$(".cThumbs").make_droppable('albums2categories');
			
			// Выделяем первую категорию
			//$('#cat0').click();
			break;
	}
}

$.fn.make_droppable = function(scope) {
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
		activeClass: 'droptome',
		hoverClass: 'drophover',
		scope: scope,
		tolerance: 'pointer'
	});
}

$.fn.make_draggable = function(scope) {
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

$.fn.editMe = function(object, jsonData) {
	currentObject = $(this).attr('id');
	
	$('#title').attr('value', jsonData.name);
	$('#description').attr('value', jsonData.description);
	
	$('#editForm').data('json', jsonData);
	$('#editForm').data('object', object);
	
	switch (object) {
		case 'images':
			$('#editForm').dialog('option', 'title', 'Edit image');
			$('#formImg').attr('src', jsonData.thumb_src);
			break;
		case 'albums':
			$('#editForm').dialog('option', 'title', 'Edit album');
			$('#formImg').attr('src', jsonData.image.thumb_src);
			break;
		case 'categories':
			$('#editForm').dialog('option', 'title', 'Edit category');
			$('#formImg').attr('src', jsonData.image.thumb_src);
			break;
	}
	
	$('#editForm').dialog('open');
}

$.fn.scrollThumbs = function(steps) {
	nElements = $(this).children().length;
	
	if (nElements > 0) {
	
		var scroll = $(this).data('scroll');
		var myHeight = $(this).children(':first').outerHeight();
	
		if (!scroll) {
			$(this).data('scroll', 0);
			scroll = 0
		} 
		
		if (9 * (scroll + steps) > -nElements && steps < 0) {
			$(this).children().animate({
				"top": "-=" + myHeight * (-steps) + "px"
			});
			$(this).data('scroll', scroll + steps);
		}
		
		if (scroll < 0 && steps > 0) {
			$(this).children().animate({
				"top": "+=" + myHeight * steps + "px"
			});
			$(this).data('scroll', scroll + steps);
		}
		
	}
}

$.fn.removeElement = function(){
	var theElement = $(this).children('.active').children('img');
	var jsonData = theElement.data('json');
	
	switch ($(this).attr('id')) {
		case 'imageThumbsUL':
			$.getJSON('php/upload.php', {action: 'removeimage', id: theElement.attr('myID')}, getRemoveStatus);
			break;
		case 'albumThumbsUL':
			$.getJSON('php/upload.php', {action: 'removealbum', id: theElement.attr('myID')}, getRemoveStatus);
			break;
		case 'categoryThumbsUL':
			$.getJSON('php/upload.php', {action: 'removecategory', id: theElement.attr('myID')}, getRemoveStatus);
			break;
	}
}

function getRemoveStatus(jsonData) {
	
	if (jsonData.result.image_id) {
		$('.iThumbs').each(function(){
			if ($(this).attr('myID') == jsonData.result.image_id) 
				$(this).parent().hide();
		});
	}
	
	if (jsonData.result.album_id) {
		$('.aThumbs').each(function(){
			if ($(this).attr('myID') == jsonData.result.album_id) 
				$(this).parent().hide();
		});
	}
	
	if (jsonData.result.category_id) {
		$('.cThumbs').each(function(){
			if ($(this).attr('myID') == jsonData.result.category_id) 
				$(this).parent().hide();
		});
	}
}

$.fn.addElement = function(){
	switch ($(this).attr('id')) {
		case 'albumThumbsUL':
			$('#formImg').hide();
			$('#editForm').data('object', 'albums');
			$('#editForm').dialog('option', 'title', 'Add new album');
			break;
		case 'categoryThumbsUL':
			$('#formImg').hide();
			$('#editForm').data('object', 'categories');
			$('#editForm').dialog('option', 'title', 'Add new category');
			break;
	}
	
	$('#editForm').dialog('open');
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
		$('#modeMove').click();
	}
}

// Убираем изображение перемещенного файла и сообщаем об этом
function displayImageAction(jsonData) {
	if (mode == 'move') {
		$('.iThumbs').each(function(){
			if ($(this).attr('myID') == jsonData.result.image_id) 
				$(this).parent().hide();
		});
	}
	
	$.gritter.add({
		title: 'Image successfully copied/moved:',
		text: jsonData.result.name,
		image: jsonData.result.thumb_src,
		sticky: false, 
		time: 8000
	});
}

function displayAlbumAction(jsonData) {
	if (mode == 'move') {
		$('.aThumbs').each(function(){
			if ($(this).attr('myID') == jsonData.result.album_id) 
				$(this).parent().hide();
		});
	}
	
	$.gritter.add({
		title: 'Album successfully copied/moved:',
		text: jsonData.result.name,
		image: jsonData.result.image.thumb_src,
		sticky: false, 
		time: 8000
	});
}
 
