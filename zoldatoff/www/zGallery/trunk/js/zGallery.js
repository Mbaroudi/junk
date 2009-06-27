var DEBUG = true;
var maxThumbs = 5;
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
	errorLog("Request sent", "red");
});

$(window).resize(function(){
	positionAll();
	DOM_image.centerImg();
	DOM_topImage.centerImg();
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
	DOM_thumbsDiv.height(thumbY + 'px');
	DOM_thumbsDiv.css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	errorLog("Page reformatted", "blue");
}

(function ($) {
	$.fn.centerImg = function() {
		var iHeight = $(this).height();	
		var dHeight = $(this).parent().height();
		var iWidth 	= $(this).width();
		var dWidth 	= $(this).parent().width();
		
		var myMargin = 0;
		
		if (dWidth > iWidth && dHeight > iHeight) {
			myMargin = (dHeight - iHeight)/2;
		}
		else if (dWidth/dHeight < iWidth/iHeight) {
			myMargin = (dHeight*iWidth - iHeight*dWidth)/(2*iWidth);
		}
		else {
			myMargin = 0;
		}
		
		$(this).css( 'margin-top', myMargin + 'px' );
     };
})(jQuery);

function fillImages(data) {
	errorLog("Request received: " + data.imagelist.length + " items", "red");
	
	//Отображаем thumbnail-ы
	var myThumbs = $('#thumbs').empty();
	for (var i=0; i<data.imagelist.length; i++){
		myThumbs.append('<li class="lithumb" id="li' + i + '"/>');
		$('#li'+i).append('<img class="thumb" id="img' + i + '"/>');
		
		imageList[i] = data.imagelist[i];
		$('#img'+i).attr('src', imageList[i].thumb_src);
		$('#img'+i).attr('number', i);
	}
	
	//Подгружаем картинки
	var tmpN = new Image();
	var tmpF = new Image();
	tmpN.num = tmpF.num = 1;
	
	tmpN.src = imageList[1].norm_src;
	//tmpF.src = imageList[1].full_src;
	
	tmpN.onload = function(){
		myNum = this.num;
		errorLog(myNum + ' loaded (norm)', "blue");
		if (myNum + 1 < imageList.length) {
			this.num = myNum + 1;
			this.src = imageList[myNum + 1].norm_src;
		} //else document.removeChild(this);
	}
	
	/*
	tmpF.onload = function(){
		myNum = this.num;
		errorLog(myNum + ' loaded (full)', "red");
		if (myNum + 1 < imageList.length) {
			this.num = myNum + 1;
			this.src = imageList[myNum + 1].full_src;
		} //else document.removeChild(this);
	}
	*/
	
	//Добавляем обработчик кликов для каждого из thumbnails-ов
	$('img.thumb').load(function(){
		$(this).centerImg();
		
		$(this).click(function(){
			var myNumber = $(this).attr('number');
			DOM_image.hide();
			$('#loader').show();
			DOM_image.attr('src', imageList[myNumber].norm_src);
			DOM_image.attr('number', myNumber);
			
			$('img.activethumb').removeClass("activethumb");
			$('li.activelithumb').removeClass("activelithumb");
			$(this).addClass("activethumb");
			$('#li'+myNumber).addClass("activelithumb");
			
			DOM_caption.html(imageList[myNumber].title);
			DOM_caption.css('display','none').fadeIn(1000);
			
			// сдвигаем активный thumb ближе к центру 
			scrollThumbs(LScroll + Math.floor(nThumbs/2) - myNumber);
		})
	})
	
	//Выставляем размеры DIV-а с thumb-ами
	liWidth = parseInt($('#li0').outerWidth()) 
				+ parseInt($('#li0').css('margin-right')) 
				+ parseInt($('#li0').css('margin-left'));
	nThumbs = Math.min( Math.floor( (maxX-leftX-rightX) / liWidth ), maxThumbs);
	LScroll = 0;
	RScroll = Math.max(0, imageList.length - nThumbs);
	
	DOM_thumbsDiv.width(nThumbs*liWidth + 'px');
	DOM_thumbsDiv.css("left", (maxX-leftX-rightX-nThumbs*liWidth)/2 + 'px'); ///!!!!
	
	//Отображаем картинку из первого thumb-а
	$('#img0').load( function(){
		$(this).click();
	});
	
	//Убираем loader image
	DOM_image.load(function(){
		$('#loader').hide();
		DOM_image.centerImg();
		DOM_image.fadeIn(1000);
	})
	
	//При клике по картинке переходим в full-screen режим
	DOM_image.click(function(){
		var myNumber = $(this).attr('number');
		
		if (DOM_topImage.attr('src') != imageList[myNumber].full_src) {
			DOM_topImage.hide();
			$('#topLoader').show();
			DOM_topImage.css('margin-top', "0px");
			DOM_topImage.attr('src', imageList[myNumber].full_src);
		}
		else {
			//DOM_topImage.fadeIn(100);
			DOM_topImage.show();
		}
		DOM_topDiv.css('display','block');
	})
	
	//Позиционируем картинку в full-screen-е по вертикали
	DOM_topImage.load(function(){
		$('#topLoader').hide();
		DOM_topImage.centerImg();
		DOM_topImage.fadeIn(1000);
	})
	
	//При клике по картинке возвращаемся к обычному просмотру
	DOM_topImage.click(function(){
		DOM_topDiv.fadeOut(1000);
	})
	
	//Скроллинг thumbs-ов
	$('#toLeft').click(function(){
		scrollThumbs(nThumbs);
	})
	
	$('#toRight').click(function(){
		scrollThumbs(-nThumbs);
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
	if (steps > 0 && LScroll >= steps) {
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

function errorLog(message, color) {
	if (DEBUG) {
		var currentTime = new Date();
		var hours = currentTime.getHours();
		var min = currentTime.getMinutes();
		var sec = currentTime.getSeconds();
		
		if (!color) color = "white";
		
		DOM_rightDiv.append('<span class="log" style="color:' + color + '">[' + hours + ':' + min + ':' + sec + '] ' + message + '<br></span>');
		
		var logDiv = document.getElementById("rightDiv");
		logDiv.scrollTop = logDiv.scrollHeight;
	}
}
