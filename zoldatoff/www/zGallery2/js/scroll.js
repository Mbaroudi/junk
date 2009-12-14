function initAlbumsScroll(){
	/* Init vertical scroll for albums */
    var $albUL = $("#albUL");
    var scrollHeight = prepareUL($albUL, 'v');
    
    $("#albUp img").click(function(){
        $albUL.scrollVertically(-1, scrollHeight);
    });
    
    $("#albDown img").click(function(){
        $albUL.scrollVertically(1, scrollHeight);
    });
	
	$albUL.scrollVertically(0, 0);
	
	$("#albUL img").hide();
	$("#albUL img").each(function(){
        return $(this).load(function(){
            $(this).parent().removeClass('loadingdiv');
            return $(this).fadeIn();
        });
    });
}

function initImagesScroll(){
	// Init horisontal scroll for images
    var $imgUL = $("#imgUL");
    var scrollWidth = prepareUL($imgUL, 'h');
    
    $("#imgLeft img").click(function(){
        $imgUL.scrollHorisontally(-1, scrollWidth);
    });
    
    $("#imgRight img").click(function(){
        $imgUL.scrollHorisontally(1, scrollWidth);
    });
	
	$imgUL.scrollHorisontally(0, 0);
	
	$("#imgUL img").hide();
    $("#imgUL img").each(function(){
        return $(this).load(function(){
            $(this).parent().removeClass('loadingdiv');
            return $(this).fadeIn();
        });
    });
}

/* Determine scrolling parameters */
function prepareUL($ul, direction){
	var scrollDelta, visibleLength;
	if (direction === 'v') {
		scrollDelta = $ul.children(":first-child").fullHeight();
		visibleLength = Math.floor($ul.parent().innerHeight() / scrollDelta);
	}
	else {
		scrollDelta = $ul.children(":first-child").fullWidth();
		visibleLength = Math.floor($ul.parent().innerWidth() / scrollDelta);
	}
	
	$ul.data("length", $ul.children().length);
	$ul.data("visibleLength", visibleLength);
    $ul.data("currentItem", 0);
	
	$ul.data('scrollDelta', scrollDelta);
	
	return scrollDelta;
}

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
    var length = $t.data("length");
    var visibleLength = $t.data("visibleLength");
    var currentItem = $t.data("currentItem");
    
    if (currentItem <= visibleLength - length && steps < 0) {
        return $t;
    }
    
    if (currentItem >= 0 && steps > 0) {
        return $t;
    }
    
    $t.data("currentItem", currentItem + steps);
    
    if (direction === 'v') {
        return $t.stop().animate({
            "top": "+=" + scrollSize * steps + "px"
        });
    }
    
    if (direction === 'h') {
        return $t.stop().animate({
            "left": "+=" + scrollSize * steps + "px"
        });
    }
};

/* Determine wether to change scrolling icons or not */
function changeIcon($ul, direction, $direction1, $direction2) {
	var length = $ul.data("length");
    var visibleLength = $ul.data("visibleLength");
    var currentItem = $ul.data("currentItem");
	
	var src1 = (direction === 'v') ? "icons/up.png" : "icons/left.png";
	var src2 = (direction === 'v') ? "icons/down.png" : "icons/right.png";
    
    if (currentItem <= visibleLength - length) {
		$direction1.hide();
    }
    else {
		$direction1.show();
    }
	
    if (currentItem >= 0) {
		$direction2.hide();
    }
    else {
		$direction2.show();
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
