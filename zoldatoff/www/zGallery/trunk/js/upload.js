/**
 * @author dsoldatov
 */

var dProgress, progress;
var currentObject, 
	currentAlbum = null, 
	currentCategory = null;
var theImageList, theAlbumList, theCategoryList;

var mode = 'move';

/* Режим работы:
 * new
 * copy
 * move
 * edit
 */

$(document).ready( function() {
	theImageList = $('#imageThumbsUL');
	theAlbumList = $('#albumThumbsUL');
	theCategoryList = $('#categoryThumbsUL');
	
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
				
				if (mode != 'edit') {
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
		return false;	
	});
	
	// Run Move mode
	$('#modeMove').click();
	
	// Init scroll interfaces
	$('#iUp').click(function(){
		theImageList.scrollThumbs(1);
		return false;
	});
	$('#iDown').click(function(){
		theImageList.scrollThumbs(-1);
		return false;
	});
	
	$('#aUp').click(function(){
		theAlbumList.scrollThumbs(1);
		return false;
	});
	$('#aDown').click(function(){
		theAlbumList.scrollThumbs(-1);
		return false;
	});
	
	$('#cUp').click(function(){
		theCategoryList.scrollThumbs(1);
		return false;
	});
	$('#cDown').click(function(){
		theCategoryList.scrollThumbs(-1);
		return false;
	});
	
	// Init remove interfaces
	$('#iRemove').click(function(){
		theImageList.removeElement();
		return false;
	});
	$('#aRemove').click(function(){
		theAlbumList.removeElement();
		return false;
	});
	$('#cRemove').click(function(){
		theCategoryList.removeElement();
		return false;
	});
	
	// Init add interfaces
	$('#modeNew').click(function(){
		mode = 'new';
		runMode();
		return false;
	});
	$('#aAdd').click(function(){
		theAlbumList.addElement();
		return false;
	});
	$('#cAdd').click(function(){
		theCategoryList.addElement();
		return false;
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
	var N;
	
	if (jsonData.result.album_id) {
		theAlbumList.children().length + 1;
		theAlbumList.append('<li><img id="alb' + N + '" class="aThumbs" src="' + jsonData.result.image.thumb_src + '"/> </li>');
		$('#alb'+N).attr('myID', jsonData.result.album_id);
		$('#alb'+N).data('json', jsonData.result);
	}
	
	if (jsonData.result.category_id) {
		theCategoryList.children().length + 1;
		theCategoryList.append('<li><img id="cat' + N + '" class="cThumbs" src="' + jsonData.result.image.thumb_src + '"/> </li>');
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
			if (!currentCategory) {
				lockDisplay();
				$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
			}
			break;
		case 'edit':
			$('#iRemove').show();
			$('#aRemove').show();
			$('#cRemove').show();
			$('#aAdd').show();
			$('#cAdd').show();
			$('#modeNew').show();
			if (!currentCategory) {
				lockDisplay();
				$.getJSON('php/upload.php', {object: 'categories'}, listCategories);
			}
			break;
		case 'new':
			$.getJSON('php/upload.php', {object: 'newimages'}, listNewImages);
			break;
	}
	
	if (mode != 'new') {
		if (currentAlbum) {
			lockDisplay();
			$.getJSON('php/upload.php', {object: 'images',album_id: currentAlbum}, listImages);
		}
		if (currentCategory) {
			lockDisplay();
			$.getJSON('php/upload.php', {object: 'albums', category_id: currentCategory}, listAlbums);
		}
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
			theImageList.empty();
			theAlbumList.empty();
			theCategoryList.empty();
			break;
		case 'images':
			if (jsonData.objectlist.image_list) {
				nObjects = jsonData.objectlist.image_list.length;
			}
			else {
				nObjects = 0;
			}
			theImageList.empty();
			$('#iCaption').html('Images from album "' + jsonData.objectlist.name + '"');
			break;
		case 'albums':
			if (jsonData.objectlist.album_list) {
				nObjects = jsonData.objectlist.album_list.length;
			}
			else {
				nObjects = 0;
			}
			theAlbumList.empty();
			$('#aCaption').html('Albums from category "' + jsonData.objectlist.name + '"');
			break;
		case 'categories':
			nObjects = jsonData.objectlist.category_list.length;
			theCategoryList.empty();
			break;
	}		
	
	//Заполняем соответствующий список
	for (var i=0; i<nObjects; i++){
		switch (object) {
			case 'newimages':
				theImageList.append('<li><img id="img' + i + '" class="iThumbs" src="css/loader.gif"/> </li>');
				break;
			case 'images':
				theImageList.append('<li><img id="img' + i + '" class="iThumbs" src="' + jsonData.objectlist.image_list[i].thumb_src + '"/> </li>');
				$('#img'+i)
					.attr('myID', jsonData.objectlist.image_list[i].image_id)
					.data('json', jsonData.objectlist.image_list[i]);
				break;
			case 'albums':
				theAlbumList.append('<li><img id="alb' + i + '" class="aThumbs" src="' + jsonData.objectlist.album_list[i].image.thumb_src + '"/> </li>');
				$('#alb'+i)
					.attr('myID', jsonData.objectlist.album_list[i].album_id)
					.data('json', jsonData.objectlist.album_list[i]);
				break;
			case 'categories':
				theCategoryList.append('<li><img id="cat' + i + '" class="cThumbs" src="' + jsonData.objectlist.category_list[i].image.thumb_src + '"/> </li>');
				$('#cat'+i)
					.attr('myID', jsonData.objectlist.category_list[i].category_id)
					.data('json', jsonData.objectlist.category_list[i]);
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
				if (mode == 'edit') 
					$('.iThumbs').parent().removeClass('active');
				$(this).parent().toggleClass('active');
				return false;
			});
			
			$('.iThumbs').dblclick( function(){
				if (mode != 'edit') $(this).editMe(object, $(this).data('json'));
				return false;
			});
			
			// Изображения можно перетаскивать внутри группы images2albums / images2all
			if (mode == 'edit') {
				$('.iThumbs').make_draggable('icon');
			}
			else 
				$('.iThumbs').make_draggable('images2albums');
			
			break;
			
		case 'albums':
			// При выделении альбома подгружаются изображения из него
			$('.aThumbs').click( function(){
				$('.aThumbs').parent().removeClass('active');
				$(this).parent().addClass('active');
				$.getJSON('php/upload.php', {object: 'images', album_id: $(this).attr('myID')}, listImages);
				currentAlbum = $(this).attr('myID');
				if (mode != 'edit') {
					$(".aThumbs").droppable('enable');
					$(this).droppable('disable');
				}
				return false;
			})
			
			$('.aThumbs').dblclick( function(){
				if (mode != 'edit') $(this).editMe(object, $(this).data('json'));
				return false;
			});
			
			// На альбомы можно перетаскивать изображения
			if (mode == 'edit') 
				$(".aThumbs").make_droppable('icon');
			else
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
				currentAlbum = null;
				currentCategory = $(this).attr('myID');
				if (mode != 'edit') {
					$(".cThumbs").droppable('enable');
					$(this).droppable('disable');
				}
				return false;
			})
			
			$('.cThumbs').dblclick( function(){
				if (mode != 'edit') $(this).editMe(object, $(this).data('json'));
				return false;
			});
									
			// На категории можно перетаскивать альбомы
			if (mode == 'edit')
				$(".cThumbs").make_droppable('icon');
			else
				$(".cThumbs").make_droppable('albums2categories');
			
			// Выделяем первую категорию
			//$('#cat0').click();
			break;
	}
	
	unlockDisplay();
}

$.fn.make_droppable = function(scope) {
	$(this).droppable({
		drop: function(event, ui) {
			lockDisplay();
			t = $(this);
			dropObjectID = t.attr('myID');
			
			// Перебираем drag'n'drop-нутые альбомы и перемещаем их в новую категорию
			// TODO: сейчас альбом удаляется изо всех категорий. Нужно действовать мягче...
			$('#draggingContainer').children().each(function() {
				$('#' + $(this).attr('id')).parent().removeClass('active');
				var dragObjectID = $(this).attr('myID');						
				
				switch (scope) {
					case 'images2albums':     
						$.getJSON('php/upload.php', {action: mode + scope, imageid: dragObjectID, albumid: dropObjectID, currentalbumid: currentAlbum}, displayImageAction);
						break;
					case 'albums2categories': 
						$.getJSON('php/upload.php', {action: mode + scope, albumid: dragObjectID, categoryid: dropObjectID, currentcategoryid: currentCategory}, displayAlbumAction);
						break;
					case 'icon': 
						if (t.hasClass('aThumbs')) 
							$.getJSON('php/upload.php', {action: mode + 'album' + scope, imageid: dragObjectID, albumid: dropObjectID}, displayThumbAction);
						if (t.hasClass('cThumbs'))
							$.getJSON('php/upload.php', {action: mode + 'category' + scope, imageid: dragObjectID, categoryid: dropObjectID}, displayThumbAction);
						currentObject = t.attr('id');
						break;
				}
			});
		},
		activeClass: 'droptome',
		hoverClass: 'drophover',
		scope: scope,
		tolerance: 'pointer'
	});
	
	return $(this);
}

$.fn.make_draggable = function(scope) {
	$(this).draggable({
		appendTo: 'body',
		containment: '#containerDiv',
		helper: function(){
			// Собираем выделенные альбомы в div и тащим...
			switch (scope) {
				case 'icon':
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
	
	return $(this);
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
	
	return $(this);
}

$.fn.scrollThumbs = function(steps) {
	var nElements = $(this).children().length;
	
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
	
	return $(this);
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
	
	return $(this);
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
	
	unlockDisplay();
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
	
	return $(this);
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
	
	unlockDisplay();
	
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
	
	unlockDisplay();
	
	$.gritter.add({
		title: 'Album successfully copied/moved:',
		text: jsonData.result.name,
		image: jsonData.result.image.thumb_src,
		sticky: false, 
		time: 8000
	});
}

function displayThumbAction(jsonData) {
	var c = $('#' + currentObject);
	
	c.attr('src', jsonData.result.image.thumb_src)
	 .data('json', jsonData.result)
	c.parent().effect('highlight', {
		color: '#dddddd'
	}, 1000);
	
	unlockDisplay();
	
	$.gritter.add({
		title: 'Album/category icon successfully changed:',
		text: jsonData.result.name,
		image: jsonData.result.image.thumb_src,
		sticky: false, 
		time: 8000
	});
}

function lockDisplay() {
	$('#lockDiv').show();
}

function unlockDisplay() {
	$('#lockDiv').hide();
}
 
