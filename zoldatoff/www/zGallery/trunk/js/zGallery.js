// TODO: remove click double-binding!!!
var DEBUG = false;
var maxThumbs = 7;
var nThumbs = maxThumbs;
var imageList = new Array();
var LScroll = 0;
var RScroll = 0;
var maxX;
var maxY;

var DOM_image;
var DOM_topImage;
var DOM_caption;

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
	DOM_caption		= $('#caption');
	
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
	$.getJSON('php/list_images.php', {gallery: 'default'}, fillImages);
	$.getJSON('php/list_images.php', {gallery: 'default'}, fillCategories);
	growl("Request sent");
	
	//Скроллинг thumbs-ов
	$('#toLeft').click(function(){
		scrollThumbs(nThumbs);
		return false;
	})
	
	$('#toRight').click(function(){
		scrollThumbs(-nThumbs);
		return false;
	})
});

$(window).resize(function(){
	positionAll();
	DOM_image.center();
	DOM_topImage.center();
})

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
	DOM_thumbsDiv
		.height(thumbY + 'px')
		.css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	growl("Page reformatted");
}

function fillSide(jsonData, side /* 'l' or 'r' */) {
	var theElement = (side == 'l') ? DOM_leftDiv : DOM_rightDiv;
	var theAction  = (side == 'l') ? fillAlbums : fillImages;
	theElement.empty();
	
	for (var i=0; i<jsonData.imagelist.length; i++){
		imageList[i] = jsonData.imagelist[i];
		
		var newDiv =  $('<div/>')
			.attr("id", side + "div" + i)
			.addClass(side + "div")
			.css("bottom", 100*i);
		
		var newImg = $("<img/>")
			.attr("id", side + "img" + i)
			.addClass("thumb")
			.attr("src", imageList[i].thumb_src)
			.attr('number', i);
		
		var newSpan = $("<span/>")
			.attr("id", side + "title" + i).addClass(side + "title")
			.html(imageList[i].title)
			.hide();
		
		newDiv
			.append(newImg)
			.append(newSpan)
			.appendTo(theElement)
			.hide();
	}
	
	var nItems = jsonData.imagelist.length;
	
	$("img", theElement).load(function() {
		$(this).center();
		if (--nItems == 0) 
			$("div", theElement)
				.fadeIn(500, function(){
					$("span", theElement).fadeIn(500)
				});
	})
	
	$("img", theElement).click(function() {
		$.getJSON('php/list_images.php', {gallery: 'default'}, theAction);
	})
	
}

function fillCategories(jsonData) {
	fillSide(jsonData, 'l');
}

function fillAlbums(jsonData) {
	fillSide(jsonData, 'r');
}

function fillImages(data) {
	growl("Request received", data.imagelist.length + " items");
	
	//Отображаем thumbnail-ы
	var myThumbs = $('#thumbs').empty();
	for (var i=0; i<data.imagelist.length; i++){
		imageList[i] = data.imagelist[i];
		
		var newLi = $('<li/>')
			.attr("id", "li" + i)
			.addClass("lithumb");
			
		var newImg = $('<img/>')
			.attr("id", "img" + i)
			.addClass("thumb")
			.attr('src', imageList[i].thumb_src)
			.attr('number', i);
			
		newLi.append(newImg).appendTo(myThumbs);
	}
	
	//Подгружаем картинки
	var tmpN = new Image();
	var tmpF = new Image();
	tmpN.num = tmpF.num = 1;
	
	tmpN.src = imageList[1].norm_src;
	//tmpF.src = imageList[1].full_src;
	
	var nItems = imageList.length;
	
	tmpN.onload = function(){
		var myNum = this.num;
		//growl(myNum + ' loaded (norm)');
		if (++myNum < nItems) {
			this.num = myNum;
			this.src = imageList[myNum].norm_src;
		}
	}
	
	/*
	tmpF.onload = function(){
		myNum = this.num;
		growl(myNum + ' loaded (full)');
		if (myNum + 1 < imageList.length) {
			this.num = myNum + 1;
			this.src = imageList[myNum + 1].full_src;
		}
	}
	*/
	
	//Добавляем обработчик кликов для каждого из thumbnails-ов
	$('#thumbsDiv img.thumb').load(function(){
		$(this).center();
		
		$(this).click(function(){
			var myNumber = $(this).attr('number');
			
			DOM_image.hide();
			$('#loader').show();
			
			DOM_image
				.attr('src', '')
				.attr('src', imageList[myNumber].norm_src)
				.attr('number', myNumber);
			
			$('img.activethumb', '#thumbs').removeClass("activethumb");
			$('li.activelithumb', '#thumbs').removeClass("activelithumb");
			$(this).addClass("activethumb");
			$('#li'+myNumber).addClass("activelithumb");
			
			DOM_caption
				.html(imageList[myNumber].title)
				.css('display','none').fadeIn(1000);
			
			// сдвигаем активный thumb ближе к центру 
			scrollThumbs(LScroll + Math.floor(nThumbs/2) - myNumber);
			
			return false;
		})
	})
	
	//Выставляем размеры DIV-а с thumb-ами
	liWidth = parseInt($('#li0').outerWidth()) 
				+ parseInt($('#li0').css('margin-right')) 
				+ parseInt($('#li0').css('margin-left'));
	nThumbs = Math.min( Math.floor( (maxX-leftX-rightX) / liWidth ), maxThumbs);
	LScroll = 0;
	RScroll = Math.max(0, imageList.length - nThumbs);
	
	DOM_thumbsDiv
		.width(nThumbs*liWidth + 'px')
		.css("left", (DOM_imagesDiv.width()-nThumbs*liWidth)/2 + 'px');
	
	//Отображаем картинку из первого thumb-а
	$('#img0').load( function(){
		$(this).click();
	});
	
	//Убираем loader image
	DOM_image.load(function(){
		$('#loader').hide();
		DOM_image.center();
		DOM_image.fadeIn(1000);
	})
	
	//При клике по картинке переходим в full-screen режим
	DOM_image.click(function(){
		var myNumber = $(this).attr('number');
		
		if (DOM_topImage.attr('src') != imageList[myNumber].full_src) {
			DOM_topImage.hide();
			$('#topLoader').show();
			DOM_topImage
				.css('margin-top', "0px")
				.attr('src', imageList[myNumber].full_src);
		}
		else {
			//DOM_topImage.fadeIn(100);
			DOM_topImage.show();
		}
		DOM_topDiv.css('display','block');
		
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

