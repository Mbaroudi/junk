var DEBUG = true;
var maxThumbs = 5;
var nThumbs = maxThumbs;
var imageList = new Array();
var LScroll = 0;
var RScroll = 0;

$(document).ready(function(){
	setInterface();
	$.getJSON('php/list_images.php', {gallery: 'default'}, fillImages);
	errorLog("Request sent", "red");
});

$(window).resize(setInterface);

function setInterface() {		
	maxX = $('body').width();
	maxY = $('body').height();
	
	headerY = $('#header').height();
	footerY = $('#footer').height();
	thumbY = $('#thumbsDiv').height();
	captionY = $('#captionDiv').height();
	arrowsY = $('#arrowsDiv').height();
	leftX = $('#leftDiv').width();
	rightX = $('#rightDiv').width();
	thumbX = $('#thumbsDiv').width();
	
	wrapY = maxY - headerY - footerY;
	containerY = wrapY - thumbY - captionY - arrowsY;
	
	//Позиционируем элементы на странице
	$('#wrapDiv').height(wrapY+'px');
	$('#containerDiv').height(containerY+'px');
	$('#imagesDiv').width(maxX-leftX-rightX+'px');
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	errorLog("Page reformatted", "blue");
}

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
	
	//Подгрузка изображений
	for (var i = 0; i < data.imagelist.length; i++) {
		var tmp = document.createElement("img");
		tmp.src = imageList[i].norm_src;
		tmp = document.createElement("img");
		tmp.src = imageList[i].full_src;
	}
	
	//Добавляем обработчик кликов для каждого из thumbnails-ов
	$('img.thumb').load(function(){
		$(this).click(function(){
			var myNumber = $(this).attr('number');
			$('#image').hide();
			$('#loader').show();
			$('#image').attr('src', imageList[myNumber].norm_src);
			$('#image').attr('number', myNumber);
			
			$('img.activethumb').removeClass("activethumb");
			$('li.activelithumb').removeClass("activelithumb");
			$(this).addClass("activethumb");
			$('#li'+myNumber).addClass("activelithumb");
			
			$('#caption').html(imageList[myNumber].title);
			$('#caption').css('display','none').fadeIn(1000);
			
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
	
	$('#thumbsDiv').width(nThumbs*liWidth + 'px');
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-nThumbs*liWidth)/2 + 'px'); ///!!!!
	
	//Отображаем картинку из первого thumb-а
	$('#img0').load( function(){
		$(this).click();
	});
	
	//Убираем loader image
	$('#image').load(function(){
		$('#loader').hide();
		
		var iHeight = $(this).height();
		var dHeight = $('#containerDiv').height() 
						- parseInt( $('#containerDiv').css('margin-top') )
						- parseInt( $('#containerDiv').css('margin-bottom') );
		
		if (iHeight < dHeight) {
			$(this).css('margin-top', (dHeight - iHeight)/2 + "px");
		}
		else {
			$(this).css('max-height', dHeight);
		}
		
		$('#image').fadeIn(1000);
	})
	
	//При клике по картинке переходим в full-screen режим
	$('#image').click(function(){
		var myNumber = $(this).attr('number');
		
		if ($('#topImage').attr('src') != imageList[myNumber].full_src) {
			$('#topImage').hide();
			$('#topLoader').show();
			$('#topImage').css('margin-top', "0px");
			$('#topImage').attr('src', imageList[myNumber].full_src);
		}
		else {
			$('#topImage').fadeIn(1000);
		}
		$('#topDiv').css('display','block');
	})
	
	//Позиционируем картинку в full-screen-е по вертикали
	$('#topImage').load(function(){
		$('#topLoader').hide();
		
		var iHeight = $(this).height();
		var dHeight = $('#topDiv').height() 
						- parseInt( $('#topDiv').css('margin-top') )
						- parseInt( $('#topDiv').css('margin-bottom') );
		var dWidth = $('#topDiv').width() 
						- parseInt( $('#topDiv').css('margin-left') )
						- parseInt( $('#topDiv').css('margin-right') )
						- parseInt( $('body').css('padding-left') )
						- parseInt( $('body').css('padding-right') );
		
		if (iHeight < dHeight) {
			$(this).css('margin-top', (dHeight - iHeight)/2 + "px");
		}
		
		$(this).css('max-height', dHeight);
		$(this).css('max-width', dWidth);
		
		$(this).fadeIn(1000);
	})
	
	//При клике по картинке возвращаемся к обычному просмотру
	$('#topImage').click(function(){
		$('#topDiv').fadeOut(1000);
	})
	
	//Скроллинг thumbs-ов
	$('#toLeft').click(function(){
		scrollThumbs(1);
	})
	
	$('#toRight').click(function(){
		scrollThumbs(-1);
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
		
		$('#rightDiv').append('<span class="log" style="color:' + color + '">[' + hours + ':' + min + ':' + sec + '] ' + message + '<br></span>');
		
		var logDiv = document.getElementById("rightDiv");
		logDiv.scrollTop = logDiv.scrollHeight;
	}
}
