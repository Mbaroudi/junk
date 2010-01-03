function initAlbumsScroll(){
	/* Init vertical scroll for albums */
	var $albUL = $("#albUL").prepareUL('v');
    var scrollHeight = $albUL.data('scrollDelta');
	
	$("#albUp img")
	.unbind('click')
	.click(function(){
        $albUL.scrollVertically(1, scrollHeight);
    });
    
    $("#albDown img")
	.unbind('click')
	.click(function(){
        $albUL.scrollVertically(-1, scrollHeight);
    });
    	
	$albUL.scrollVertically(0, 0);
	
	$("#albUL img")
	.hide()
	.each(function(){
        return $(this).load(function(){
            $(this).parent().removeClass('loadingdiv_');
            return $(this).fadeIn();
        });
    });
}

function initImagesScroll(){
	// Init horisontal scroll for images
	var $imgUL = $('#imgUL').prepareUL('h');
    var scrollWidth = $imgUL.data('scrollDelta');
	
	$('#imgLeft img')
	.unbind('click')
	.click(function(){
        $imgUL.scrollHorisontally(1, scrollWidth);
    });
	
	$('#imgRight img')
	.unbind('click')
	.click(function(){
        $imgUL.scrollHorisontally(-1, scrollWidth);
    });
	
    $imgUL.scrollHorisontally(0, 0);
	
	$('#imgUL img')
	.hide()
	.each(function(){
    	return $(this).load(function(){
        	$(this).parent().removeClass('loadingdiv_');
        	return $(this).fadeIn();
    	});
	});
}

/* Determine scrolling parameters */
$.fn.prepareUL = function(direction) {
	var scrollDelta, visibleLength;
	var $ul = $(this);
	
	if (direction === 'v') {
		scrollDelta = $ul.children(":first-child").fullHeight();
		visibleLength = Math.floor($ul.parent().innerHeight() / scrollDelta);
	}
	else {
		scrollDelta = $ul.children(":first-child").fullWidth();
		visibleLength = Math.floor($ul.parent().innerWidth() / scrollDelta);
	}
	
	$ul
		.data('length', $ul.children().length)
		.data('visibleLength', visibleLength)
    	.data('currentItem', 0)
		.data('scrollDelta', scrollDelta);
	
	return $ul;
};

$.fn.fullHeight = function(){
    return parseInt($(this).outerHeight(), 10) +
    parseInt($(this).css("margin-top"), 10) +
    parseInt($(this).css("margin-bottom"), 10);
};

$.fn.fullWidth = function(){
    return parseInt($(this).outerWidth(), 10) +
    parseInt($(this).css("margin-left"), 10) +
    parseInt($(this).css("margin-right"), 10);
};

$.fn.scroll = function(steps, scrollSize, direction){
    var $t = $(this);
    var length = $t.data('length');
    var visibleLength = $t.data('visibleLength');
    var currentItem = $t.data('currentItem');
	
	if (steps === 0) {
		return $t;
	}

	if (currentItem + steps > length && steps > 0) {
        return $t.scroll(steps-1, scrollSize, direction);
    }
	
	if (currentItem - steps < -length && steps < 0) {
        return $t.scroll(steps+1, scrollSize, direction);
    }
    
    $t.data('currentItem', currentItem + steps);
    
    if (direction === 'v') {
        return $t.stop().animate({
            'top': '+=' + scrollSize * steps + 'px'
        });
    }
    
    if (direction === 'h') {
        return $t.stop().animate({
            'left': '+=' + scrollSize * steps + 'px'
        });
    }
};

/* Determine wether to change scrolling icons or not */
function changeIcon($ul, direction, $direction1, $direction2) {
	var length = $ul.data('length');
    var visibleLength = $ul.data('visibleLength');
    var currentItem = $ul.data('currentItem');
	
	var src1 = (direction === 'v') ? 'icons/up.png' : 'icons/left.png';
	var src2 = (direction === 'v') ? 'icons/down.png' : 'icons/right.png';
	
	var d = (direction === 'v') ? 1 : 4;
    
    if (currentItem <= d - length) {
		$direction2.hide();
    }
    else {
		$direction2.show();
    }
	
    if (currentItem >= visibleLength - d) {
		$direction1.hide();
    }
    else {
		$direction1.show();
    }
	
	return $ul;
}

$.fn.scrollVertically = function(steps, scrollHeight){
	var $t = $(this).scroll(steps, scrollHeight, 'v');
	return changeIcon($t, 'v', $('#albUp img'), $("#albDown img"));
};

$.fn.scrollHorisontally = function(steps, scrollWidth){
    var $t = $(this).scroll(steps, scrollWidth, 'h');
	return changeIcon($t, 'h', $('#imgLeft img'), $("#imgRight img"));
};
