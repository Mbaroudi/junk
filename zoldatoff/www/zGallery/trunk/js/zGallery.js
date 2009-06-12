var DEBUG = true;

var imageList = new Array();
var myImg = new Array();
var output;

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
	for (var i=0; (i<data.imagelist.length) && (i<10); i++){
		myThumbs.append('<li class="lithumb" id="li' + i + '"/>');
		$('#li'+i).append('<img class="thumb" id="img' + i + '"/>');
		
		imageList[i] = data.imagelist[i];
		$('#img'+i).attr('src', data.imagelist[i].thumb_src);
		$('#img'+i).attr('number', i);
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
			$(this).addClass("activethumb");
			
			$('#caption').html(imageList[myNumber].title);
			$('#caption').css('display','none').fadeIn(1000);
			
			errorLog("Image " + imageList[myNumber].number + " clicked", "white");
		})
	})
	
	//Выставляем размеры DIV-а с thumb-ами
	$('#thumbsDiv').css("width", data.imagelist.length*78 + 'px'); //!!!!!!!!!
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-data.imagelist.length*78)/2 + 'px'); ////!!!!
	
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



$(document).ready(setInterface);
$(document).resize(setInterface); //TODO: Why is it not working!!??
