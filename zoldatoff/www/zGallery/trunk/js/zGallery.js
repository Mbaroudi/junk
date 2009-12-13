var DEBUG = false;
var maxThumbs = 7;
var nThumbs = maxThumbs;
var LScroll = 0;
var RScroll = 0;
var maxX;
var maxY;

var DOM_image;
var DOM_topImage;

var DOM_wrapDiv;
var DOM_leftDiv;
var DOM_rightDiv;
var DOM_arrowsDiv;
var DOM_imagesDiv;
var DOM_containerDiv;
var DOM_thumbsDiv;
var DOM_arrowsDiv;
var DOM_topDiv;

$(document).ready(function(){
	DOM_image 		= $('#image');
	DOM_topImage 	= $('#topImage');
	
	DOM_wrapDiv 	= $('#wrapDiv');
	DOM_leftDiv		= $('#leftDiv');
	DOM_rightDiv	= $('#rightDiv');
	DOM_imagesDiv	= $('#imagesDiv');
	DOM_containerDiv = $('#containerDiv');
	DOM_captionDiv	= $('#captionDiv');
	DOM_thumbsDiv 	= $('#thumbsDiv');
	DOM_arrowsDiv	= $('#arrowsDiv');
	DOM_topDiv		= $('#topDiv');
	
	positionAll();
	//$.getJSON('php/list_images.php', {gallery: 'default'}, fillImages);
	$.getJSON(ajaxPath, {object: 'categories'}, fillCategories);
	
	//Скроллинг thumbs-ов
	$('#toLeft').click(function(){
		scrollThumbs(nThumbs);
		return false;
	})
	
	$('#toRight').click(function(){
		scrollThumbs(-nThumbs);
		return false;
	})
	
	//Позиционируем картинку в full-screen-е по вертикали
	DOM_topImage.load(function(){
		$('#topLoader').hide();
		DOM_topImage.center();
		DOM_topImage.fadeIn(1000);
	})
	
	//При клике по картинке возвращаемся к обычному просмотру
	DOM_topImage.click(function(){
		DOM_topDiv.fadeOut(1000);
		return false;
	})
});

$(window).resize(positionAll)

function positionAll() {		
	maxX 		= $('body').width();
	maxY 		= $('body').height();
	
	headerY 	= $('#header').outerHeight();
	footerY 	= $('#footer').outerHeight();
	thumbY		= DOM_thumbsDiv.height();
	captionY 	= DOM_captionDiv.height();
	arrowsY 	= DOM_arrowsDiv.height();
	leftX 		= DOM_leftDiv.width();
	rightX 		= DOM_rightDiv.width();
	thumbX 		= DOM_thumbsDiv.width();
	
	wrapY 		= maxY - headerY - footerY;	
	containerY	= wrapY - thumbY - captionY - arrowsY
					- parseInt(DOM_containerDiv.css('margin-top'))
					- parseInt(DOM_wrapDiv.css('border-top-width'))
					- parseInt(DOM_wrapDiv.css('border-bottom-width'));
	
	//Позиционируем элементы на странице
	DOM_wrapDiv.height(wrapY+'px');
	DOM_containerDiv.height(containerY+'px');
	DOM_imagesDiv.width(maxX-leftX-rightX+'px');
	DOM_thumbsDiv.css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	DOM_image.center();
	DOM_topImage.center();
}

function fillSide(jsonData, side /* 'l' or 'r' */) {
	var theElement = (side == 'l') ? DOM_leftDiv : DOM_rightDiv;
	var theAction  = (side == 'l') ? fillAlbums : fillImages;
	theElement.empty();
	
	var theList = (side == 'l') ? jsonData.objectlist.category_list : jsonData.objectlist.album_list;
	var nItems = theList.length;
	
	for (var i=0; i<nItems; i++){
		var newDiv =  $('<div/>')
			.attr("id", side + "div" + i)
			.addClass(side + "div")
			.css("top", 100*i+20)
			.data("object", theList[i]);
		
		var newImg = $("<img/>")
			.attr("id", side + "img" + i)
			.addClass("thumb")
			.attr("src", theList[i].image.thumb_src)
			.hide();
			
		var newImgBW = $('<img/>')
			.attr("id", side + "imgBW" + i)
			.addClass("thumbBW")
			.attr('src', theList[i].image.thumb_bw_src)
			.hide();
		
		var newSpan = $("<span/>")
			.attr("id", side + "title" + i).addClass(side + "title")
			.html(theList[i].name)
			.hide();
		
		newDiv
			.append(newImg)
			.append(newImgBW)
			.append(newSpan)
			.appendTo(theElement)
			.hide();
	}
	
	$("img.thumb", theElement).load(function() {
		$(this).center();
	})
	
	$("img.thumbBW", theElement).load(function() {
		$(this).center().show();
		
		$(this).parent().fadeIn(500, function(){
			$("span", theElement).fadeIn(500)
		});
	})
	
	$("div", theElement)
		.click(function() {
				$('span', theElement).removeClass("activetitle");
				$('span', $(this)).addClass("activetitle");
				
				$('div', theElement).removeClass("active");
				$(this).addClass("active");
				
				$('.thumb', theElement).hide();
				$('.thumbBW', theElement).show();
				$('.thumb', $(this)).show();
				$('.thumbBW', $(this)).hide();
				
				var myID = (side == 'l') ? $(this).data('object').category_id : $(this).data('object').album_id;
				switch (side) {
					case 'l':
						$.getJSON(ajaxPath, {object: 'albums', category_id: myID}, theAction);
						break;
					case 'r':
					 	$.getJSON(ajaxPath, {object: 'images', album_id: myID}, theAction);
						break;
				}
			}
		)
		.hover( function(){
			 	if (!$(this).hasClass("active")) {
					$(this).children().filter('.thumb').show();
					$(this).children().filter('.thumbBW').hide();
				}
			},
			function(){
				if (!$(this).hasClass("active")) {
					$(this).children().filter('.thumb').hide();
					$(this).children().filter('.thumbBW').show();
				}
			}
		)
	
	$('span', theElement).click(function(){
		$(this).parent().click();
	})
	
	$("#"+side+"div0").click();
}

function fillCategories(jsonData) {
	fillSide(jsonData, 'l');
}

function fillAlbums(jsonData) {
	fillSide(jsonData, 'r');
}

function fillImages(data) {
	var imagelist = data.objectlist.image_list;
	var nItems = imagelist.length;
	//growl("Request received", nItems + " items");
	
	//Отображаем thumbnail-ы
	var myThumbs = $('#thumbs').empty();
	for (var i=0; i<nItems; i++){		
		var newLi = $('<li/>')
			.attr("id", "li" + i)
			.addClass("lithumb")
			.data('image', imagelist[i])
			.data('number', i);
			
		var newImg = $('<img/>')
			.attr("id", "img" + i)
			.addClass("thumb")
			.attr('src', imagelist[i].thumb_src)
			.hide();
		
		var newImgBW = $('<img/>')
			.attr("id", "imgBW" + i)
			.addClass("thumbBW")
			.attr('src', imagelist[i].thumb_bw_src)
			.hide();
			
		newLi.append(newImg).append(newImgBW).appendTo(myThumbs);
	}
	
	//Подгружаем картинки
	/*var num = 1;
	imageList = data.imagelist;
	$('<img/>')
		.attr('src', data.imagelist[1].norm_src)
		.load( function(){
			//growl(num + ' loaded (norm)');
			if (++num < nItems) $(this).attr('src', imageList[num].norm_src);
		})
	*/
	
	//Добавляем обработчик кликов для каждого из thumbnails-ов
	$('#thumbs img.thumb').load(function(){
		$(this).center();
	})
	
	$('#thumbs img.thumbBW').load(function(){
		$(this)
			.center()
			.css('z-index', '1000')
			.fadeIn()
	})
	
	$('#thumbs li')
		.click( function(){
				var t = $(this);
				
				var myNumber = t.data('number');
				var imageData = t.data('image');
				
				DOM_image
					.hide()
					.attr('src', '')
					.attr('src', imageData.norm_src)
					.data('image', imageData);
				
				$('#loader').show();
				
				myLi = $('#thumbs li.activelithumb');
				myLi.removeClass("activelithumb");
				myLi.children().filter('.thumb').hide();
				myLi.children().filter('.thumbBW').show();
				
				t.addClass("activelithumb");
				
				$('#caption').html(imageData.name).hide().fadeIn(1000);
				
				// сдвигаем активный thumb ближе к центру 
				scrollThumbs(LScroll + Math.floor(nThumbs/2) - myNumber);
				
				return false;
			}
		)
		.hover( function(){
			 	if (!$(this).hasClass("activelithumb")) {
					$(this).children().filter('.thumb').show();
					$(this).children().filter('.thumbBW').hide();
				}
			},
			function(){
				if (!$(this).hasClass("activelithumb")) {
					$(this).children().filter('.thumb').hide();
					$(this).children().filter('.thumbBW').show();
				}
			}
		);
	
	//Выставляем размеры DIV-а с thumb-ами
	liWidth = parseInt($('#li0').outerWidth()) 
				+ parseInt($('#li0').css('margin-right')) 
				+ parseInt($('#li0').css('margin-left'));
	nThumbs = Math.min( Math.min( Math.floor( (maxX-leftX-rightX) / liWidth ), maxThumbs), imagelist.length);
	LScroll = 0;
	RScroll = Math.max(0, nItems - nThumbs);
	
	DOM_thumbsDiv
		.width(nThumbs*liWidth + 'px')
		.css("left", (DOM_imagesDiv.width()-nThumbs*liWidth)/2 + 'px');
	
	//Отображаем картинку из первого thumb-а
	$('#imgBW0').load( function(){
		$(this).click();
	});
	
	//Убираем loader image
	DOM_image.unbind('load');
	DOM_image.load(function(){
		$('#loader').hide();
		DOM_image.center();
		DOM_image.fadeIn(1000);
	})
	
	//При клике по картинке переходим в full-screen режим
	DOM_image.unbind('click');
	DOM_image.click(function(){
		var imageData = $(this).data('image');
		
		if (DOM_topImage.attr('src') != imageData.full_src) {
			DOM_topImage.hide();
			$('#topLoader').show();
			DOM_topImage
				.css('margin-top', "0px")
				.attr('src', imageData.full_src);
		}
		else {
			DOM_topImage.show();
		}
		DOM_topDiv.show();
		
		return false;
	})
}

function scrollThumbs(steps) {
	//хотим и можем сдвинуться влево
	if (steps < 0 && RScroll >= -steps) {
		$('.lithumb').animate({
			"left": "-=" + liWidth * (-steps) + "px"
		});
		LScroll -= steps;
		RScroll += steps;
	}
	//хотим, но не можем сдвинуться влево
	else if (steps < 0 && RScroll < -steps) {
		scrollThumbs(steps+1);
	}
	//хотим и можем сдвинуться вправо
	else if (steps > 0 && LScroll >= steps) {
		$('.lithumb').animate({
			"left": "+=" + liWidth * steps + "px"
		});
		LScroll -= steps;
		RScroll += steps;
	}
	//хотим, но не можем сдвинуться вправо
	else if (steps > 0 && LScroll < steps) {
		scrollThumbs(steps-1);
	}
}

