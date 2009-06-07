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
	wrapY = maxY-headerY-footerY;
	containerY = wrapY - thumbY - captionY;
	wrapperY = containerY - captionY;
	
	$('#wrapDiv').height(wrapY+'px');
	$('#containerDiv').height(containerY+'px');
	$('#imagesDiv').width(maxX-leftX-rightX+'px');
	
	thumbX = $('#thumbsDiv').width();
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	errorLog("Page reformatted", "blue");
	
	$.getJSON('php/list_images.php', {gallery: 'default'}, fillImages);
}

function fillImages(data) {
	myThumbs = $('#thumbs').empty();
	
	for (var i=0; (i<data.imagelist.length) && (i<10); i++){
		myThumbs.append('<li class="lithumb" id="li' + i + '"> </li>');
		myLi = $('#li'+i);
		myLi.attr('id', 'li' + i);
		
		myLi.append('<img class="thumb" id="img' + i + '"');
		imageList[data.imagelist[i].thumb_src] = data.imagelist[i];
		myImg[i] = $('#img'+i);
		myImg[i].number
		myImg[i].attr('src', data.imagelist[i].thumb_src);
		
		//$(#caption).html(data.imagelist[i].title);
		//myImg[i].attr('alt', data.imagelist[i].title);
		//myImg[i].attr('title', data.imagelist[i].title);
	}
	
	$('img.thumb').load(function(){
		$(this).click(function(){
			var mysrc = $(this).attr('src');
			$('#image').attr('src', imageList[mysrc].norm_src);
			$('#image').css('display','none').fadeIn(1000);
		})
	})
	
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-data.imagelist.length*78)/2 + 'px');
}

$(document).ready(setInterface);
$(document).resize(setInterface);

function errorLog(message, color) {
	var currentTime = new Date();
  	var hours = currentTime.getHours();
  	var min = currentTime.getMinutes();
	var sec = currentTime.getSeconds();

	$('#rightDiv').append('<span class="log" style="color:' + color + '">[' + hours + ':' + min + ':' + sec + '] ' + message + '</span>');
}
