var DEBUG = true;
var maxThumbs = 5;
var imageList = new Array();
var LScroll = 0;
var RScroll = 0;

$(document).ready(setInterface);
$(window).resize(setInterface);

function setInterface() {		
	maxX = $('body').width();
	maxY = $('body').height();
	
	headerY = $('#header').height();
	footerY = $('#footer').height();
	thumbY = $('#thumbsDiv').height();
	captionY = $('#captionDiv').height();
	leftX = $('#leftDiv').width();
	rightX = $('#rightDiv').width();
	thumbX = $('#thumbsDiv').width();
	wrapY = maxY-headerY-footerY;
	containerY = wrapY - thumbY - captionY;
	wrapperY = containerY - captionY; 
	
	//Позиционируем элементы на странице
	$('#wrapDiv').height(wrapY+'px');
	$('#containerDiv').height(containerY+'px');
	$('#imagesDiv').width(maxX-leftX-rightX+'px');
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	errorLog("Page reformatted", "blue");
	
	$.getJSON('php/list_images.php', {gallery: 'default'}, fillImages);
	errorLog("Request sent", "red");
}

function fillImages(data) {
	var myThumbs = $('#thumbs').empty();
	
	//Отображаем thumbnail-ы
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
	
	errorLog("Request received: " + data.imagelist.length + " items", "red");
	
	//Добавляем обработчик кликов для каждого из thumbnails-ов
	$('img.thumb').load(function(){
		$(this).click(function(){
			var myNumber = $(this).attr('number');
			$('#image').attr('src', imageList[myNumber].norm_src);
			$('#image').attr('number', myNumber);
			$('#image').css('display','none').fadeIn(1000);
			
			$('img.activethumb').removeClass("activethumb");
			$('li.activelithumb').removeClass("activelithumb");
			$(this).addClass("activethumb");
			$('#li'+myNumber).addClass("activelithumb");
			
			$('#caption').html(imageList[myNumber].title);
			$('#caption').css('display','none').fadeIn(1000);
			
			errorLog("Image " + imageList[myNumber].number + " clicked", "white");
		})
	})
	
	//Выставляем размеры DIV-а с thumb-ами
	var liWidth = parseInt($('#li0').outerWidth()) 
				+ parseInt($('#li0').css('margin-right')) 
				+ parseInt($('#li0').css('margin-left'));
	var nThumbs = Math.min( Math.floor( (maxX-leftX-rightX) / liWidth ), maxThumbs);
	LScroll = 0;
	RScroll = Math.max(0, imageList.length - nThumbs);
	
	errorLog("lScroll = " + LScroll, "white");
	errorLog("rScroll = " + RScroll, "white");
	
	$('#thumbsDiv').width(nThumbs*liWidth + 'px');
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-nThumbs*liWidth)/2 + 'px');
	
	//Отображаем картинку из первого thumb-а
	$('#img0').load( function(){
		$(this).click();
	});
	
	//При клике по картинке переходим в full-screen режим
	$('#image').click(function(){
		var myNumber = $(this).attr('number');
		
		$('#topImage').css('margin-top', "0px");
		$('#topImage').attr('src',imageList[myNumber].full_src);
		$('#topDiv').css('display','block');
		$('#topImage').css('display','none').fadeIn(1000);
	})
	
	//Позиционируем картинку в full-screen-е по вертикали
	$('#topImage').load(function(){
		var iHeight = $(this).height();
		var dHeight = $('#topDiv').height();
		
		if (iHeight < dHeight) {
			$(this).css('margin-top', (dHeight - iHeight)/2 + "px");
		}
	})
	
	//При клике по картинке возвращаемся к обычному просмотру
	$('#topImage').click(function(){
		$('#topDiv').css('display','block').fadeOut(1000);
	})
	
	//Скроллинг thumbs-ов
	$('#leftDiv').click(function(){
		if (RScroll > 0) {
			$('.lithumb').animate({"left": "-=" + liWidth + "px"});
			LScroll += 1;
			RScroll -=1;
		}
	})
	
	$('#rightDiv').click(function(){
		if (LScroll > 0)  {
			$('.lithumb').animate({"left": "+=" + liWidth + "px"});
			LScroll -= 1;
			RScroll +=1;
		}
	})
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
