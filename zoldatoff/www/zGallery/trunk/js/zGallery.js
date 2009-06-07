function interface() {		
	maxX = $('body').width();
	maxY = $('body').height();
	
	headerY = $('#header').height();
	footerY = $('#footer').height();
	thumbY = $('#thumbsDiv').height();
	thumbX = $('#thumbsDiv').width();
	captionY = $('#captionDiv').height();
	leftX = $('#leftDiv').width();
	rightX = $('#rightDiv').width();
	wrapY = maxY-headerY-footerY;
	containerY = wrapY - thumbY - captionY;
	wrapperY = containerY - captionY;
	
	$('#wrapDiv').height(wrapY+'px');
	$('#containerDiv').height(containerY+'px');
	$('#imagesDiv').width(maxX-leftX-rightX+'px');
	
	$('#thumbsDiv').css("left", (maxX-leftX-rightX-thumbX)/2 + 'px');
	
	$('img.thumb').load(function(){
		$(this).click(function(){
			var mysrc = $(this).attr('src');
			$('#image').attr('src', mysrc);
			$('#image').css('display','none').fadeIn(1000);
		})
	})
	
/*
	$('#image').load(function(){
		alert($(this).height());
	})
*/
}

$(document).ready(interface);
$(document).resize(interface);