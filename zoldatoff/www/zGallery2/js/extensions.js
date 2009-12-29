/**
 * @author zoldatoff
 */

var ajaxPath = 'php/upload.php';

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
};

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
						if (t.hasClass('aThumbs')) {
							$.getJSON(ajaxPath, {
								action: mode + 'album' + scope,
								imageid: dragObjectID,
								albumid: dropObjectID
							}, displayThumbAction);
						}
						if (t.hasClass('cThumbs')) {
							$.getJSON(ajaxPath, {
								action: mode + 'category' + scope,
								imageid: dragObjectID,
								categoryid: dropObjectID
							}, displayThumbAction);
						}
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
};

$.fn.make_draggable = function(scope) {
	$(this).draggable({
		appendTo: 'body',
		containment: '#containerDiv',
		delay: 100,
		//distance: 10, 
		helper: function(){
			var selected;
			// Собираем выделенные альбомы в div и тащим...
			switch (scope) {
				case 'icon':
				case 'images2albums':     
					selected = $('#imageThumbsUL .active img');
					break;
				case 'albums2categories': 
					selected = $('#albumThumbsUL .active img');
					break;
			}
			
			if (selected.length === 0) {
				selected = $(this);
			}
			
			var myImages = selected.clone().css('position', 'static');
			
			return $('<div/>').attr('id', 'draggingContainer').append(myImages); 
		},
		opacity: 0.5,
		revert: 'invalid',
		scope: scope
	});
	
	return $(this);
};

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
};

$.fn.scrollThumbs = function(steps) {
	var t = $(this);
	
	var nElements = t.children().length;
	
	if (nElements > 0) {
	
		var scroll = t.data('scroll');
		var myHeight = t.children(':first').outerHeight();
	
		if (!scroll) {
			t.data('scroll', 0);
			scroll = 0;
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
};

$.fn.removeElement = function(){
	console.info('removing element');
	console.info($(this));
	var theElement = $(this).children('li.active').children('img');
	console.info(theElement.length);
	
	if (theElement.length) {
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
	else {
		growl('No data to remove', 'Select something to remove');
	}
	
	return $(this);
};

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
};

$.fn.highlightMe = function() {
	return $(this)
		.parent()
		.effect('highlight', { color: '#ff0000' }, 1000);
};

function growl(myTitle, myText, myImage) {
	if (!myTitle) {
		myTitle = " ";
	}
	if (!myText) {
		myText = " ";
	}
	if (!myImage) {
		myImage = "css/new.jpg";
	}
	
	$.gritter.add({
		title: myTitle,
		text: myText,
		image: myImage,
		sticky: false, 
		time: 8000
	});
}

