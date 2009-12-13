/**
 * @author Zoldatoff zoldatoff@gmail.com
 * @version 0.1 alpha
 */

/*
 * Title: jQuery extensions for zGallery
 */

/*
 * Constant: ajaxPath
 * ------------------
 * Contains the relative path to server-side script  
 */
var ajaxPath = 'php/upload.php';

/*
 * Function: center
 * ----------------
 * Centers the image within its parent element
 * 
 * Returns: 
 * 		Original jQuery object
 * 
 * Variables:
 * 		iHeight - image height
 * 		iWidth - image width
 * 		dHeight - parent height
 * 		dWidth - parent width
 * 		myTop - final image top position
 * 		myLeft - final iage left position
 */
$.fn.center = function() {
	var t = $(this);
	var iHeight = t.height() ? t.height() : t[0].height;	
	var dHeight = t.parent().height();
	var iWidth 	= t.width() ? t.width() : t[0].width;
	var dWidth 	= t.parent().width();
	
	var myTop = 0;
	var myLeft = 0;
	
	if (dWidth > iWidth && dHeight > iHeight) {
		myTop = (dHeight - iHeight) / 2;
		myLeft = (dWidth - iWidth) / 2;
	}

	else if (dWidth / dHeight < iWidth / iHeight) {
		myTop = (dHeight * iWidth - iHeight * dWidth) / (2 * iWidth);
	} 
	
	else if (dWidth / dHeight > iWidth / iHeight) {
		myLeft = (dWidth * iHeight - iWidth * dHeight) / (2 * iHeight);
	}
	
	return t
		.css('position', 'absolute')
		.css('top', myTop + 'px')
		.css('left', myLeft + 'px');
}

/*
 * Function: make_droppable
 * ------------------------
 * 
 * Implements the *jQuery UI* droppable method to the element.
 * Works within the scope.
 * 
 * Parameters:
 * 		scope - The name of the scope. Can obtain the following values:
 * 		- images2albums
 * 		- albums2categories
 * 		- icon
 * 
 * Returns:
 * 		Original *jQuery* object
 * 
 * See also:
 * 		<make_draggable>
 */
$.fn.make_droppable = function(scope) {
	$(this).droppable({
		drop: function(event, ui) {
			lockDisplay();
			t = $(this);
			dropObjectID = t.attr('myID');
			
			// Перебираем drag'n'drop-нутые альбомы и перемещаем их в новую категорию
			$('#draggingContainer').children().each(function() {
				$('#' + $(this).attr('id')).parent().removeClass('active');
				var dragObjectID = $(this).attr('myID');						
				
				switch (scope) {
					case 'images2albums':     
						$.getJSON(ajaxPath, {action: mode + scope, imageid: dragObjectID, albumid: dropObjectID, currentalbumid: currentAlbum}, displayDropStatus);
						break;
					case 'albums2categories': 
						$.getJSON(ajaxPath, {action: mode + scope, albumid: dragObjectID, categoryid: dropObjectID, currentcategoryid: currentCategory}, displayDropStatus);
						break;
					case 'icon': 
						if (t.hasClass('aThumbs')) 
							$.getJSON(ajaxPath, {action: mode + 'album' + scope, imageid: dragObjectID, albumid: dropObjectID}, displayThumbAction);
						if (t.hasClass('cThumbs'))
							$.getJSON(ajaxPath, {action: mode + 'category' + scope, imageid: dragObjectID, categoryid: dropObjectID}, displayThumbAction);
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

/*
 * Function: make_draggable
 * ------------------------
 * 
 * Implements the *jQuery UI* draggable method to the element.
 * Works within the scope.
 * 
 * Parameters:
 * 		scope - The name of the scope. Can obtain the following values:
 * 		- images2albums
 * 		- albums2categories
 * 		- icon
 * 
 * Returns:
 * 		Original *jQuery* object
 * 
 * See also:
 * 		<make_droppable>
 */
$.fn.make_draggable = function(scope) {
	$(this).draggable({
		appendTo: 'body',
		containment: '#containerDiv',
		delay: 100,
		//distance: 10, 
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
			
			if (selected.length == 0) selected = $(this);
			
			var myImages = selected.clone().css('position', 'static');
			
			return $('<div/>').attr('id', 'draggingContainer').append(myImages); 
		},
		opacity: 0.5,
		revert: 'invalid',
		scope: scope
	});
	
	return $(this);
}

/*
 * Function: editMe
 * ------------------------
 * 
 * Sets the EditDialog properties and opens the dialog
 * 
 * Parameters:
 * 		object - The type of the object, which parameters will be edited.
 * 		Can obtain the following values:
 * 		- images
 * 		- albums
 * 		- categories
 * 
 * 		jsonData - Data, related to editing object
 * 
 * Returns:
 * 		Original *jQuery* object
 * 
 * See also:
 * 		<addElement>
 */
$.fn.editMe = function(object, jsonData) {
	currentObject = $(this).attr('id');
	
	$('#title').attr('value', jsonData.name);
	$('#description').attr('value', jsonData.description);
	
	theEditForm
		.data('json', jsonData)
		.data('object', object);
	
	switch (object) {
		case 'images':
			theEditForm.dialog('option', 'title', 'Edit image');
			theFormImg.attr('src', jsonData.thumb_src);
			break;
		case 'albums':
			theEditForm.dialog('option', 'title', 'Edit album');
			theFormImg.attr('src', jsonData.image.thumb_src);
			break;
		case 'categories':
			theEditForm.dialog('option', 'title', 'Edit category');
			theFormImg.attr('src', jsonData.image.thumb_src);
			break;
	}
	
	theEditForm.dialog('open');
	
	return $(this);
}

/**
 * @namespace $
 * @classDescription Scrolls the thumbs on admin panel several steps up or down
 * @method
 * @param {Number} steps Number of steps to scroll
 * @return {$} original jQuery object
 */
$.fn.scrollThumbs = function(steps) {
	var t = $(this);
	
	var nElements = t.children().length;
	
	if (nElements > 0) {
	
		var scroll = t.data('scroll');
		var myHeight = t.children(':first').outerHeight();
	
		if (!scroll) {
			t.data('scroll', 0);
			scroll = 0
		} 
		
		if (9 * (scroll + steps) > -nElements && steps < 0) {
			t.children().animate({
				"top": "-=" + myHeight * (-steps) + "px"
			});
			t.data('scroll', scroll + steps);
		}
		
		if (scroll < 0 && steps > 0) {
			t.children().animate({
				"top": "+=" + myHeight * steps + "px"
			});
			t.data('scroll', scroll + steps);
		}
		
	}
	
	return t;
}

/**
 * @namespace $
 * @classDescription Sends AJAX request to server side to remove an element
 * @method
 * @return {$} original jQuery object
 */
$.fn.removeElement = function(){
	var theElement = $('li.active img', $(this));
	
	if (theElement.length != 0) {
		var jsonData = theElement.data('json');
		
		switch ($(this).attr('id')) {
			case 'imageThumbsUL':
				$.getJSON(ajaxPath, {
					action: 'removeimage',
					id: theElement.attr('myID'),
					albumid: currentAlbum
				}, getRemoveStatus);
				break;
			case 'albumThumbsUL':
				$.getJSON(ajaxPath, {
					action: 'removealbum',
					id: theElement.attr('myID'),
					categoryid: currentCategory
				}, getRemoveStatus);
				break;
			case 'categoryThumbsUL':
				$.getJSON(ajaxPath, {
					action: 'removecategory',
					id: theElement.attr('myID')
				}, getRemoveStatus);
				break;
		}
		
		lockDisplay();
	}
	else 
		growl('No data to remove', 'Select something to remove')
	
	return $(this);
}

/**
 * @namespace $
 * @classDescription Opens a dialog for filling-in new element parameters
 * @method
 * @return {$} original jQuery object
 */
$.fn.addElement = function(){
	switch ($(this).attr('id')) {
		case 'albumThumbsUL':
			theFormImg.hide();
			theEditForm
				.data('object', 'albums')
				.dialog('option', 'title', 'Add new album');
			break;
		case 'categoryThumbsUL':
			theFormImg.hide();
			theEditForm
				.data('object', 'categories')
				.dialog('option', 'title', 'Add new category');
			break;
	}
	
	theEditForm.dialog('open');
	
	return $(this);
}

/**
 * @namespace $
 * @classDescription Highlights an element's parent
 * @method
 * @return {$} original jQuery object
 */
$.fn.highlightMe = function() {
	return $(this)
		.parent()
		.effect('highlight', { color: '#ff0000' }, 1000);
}

/**
 * @namespace $
 * @classDescription Opens a growl-like message window
 * @param {String} myTitle The title of the window
 * @param {String} myText Optional. The message in the window
 * @param {String} myImage Optional. Path to an image to display in the message
 */
function growl(myTitle, myText, myImage) {
	if (!myTitle) myTitle = " ";
	if (!myText) myText = " ";
	if (!myImage) myImage = "css/new.jpg";
	
	$.gritter.add({
		title: myTitle,
		text: myText,
		image: myImage,
		sticky: false, 
		time: 8000
	});
}

