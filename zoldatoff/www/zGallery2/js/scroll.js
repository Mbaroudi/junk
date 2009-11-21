$(document).ready(function(){
	
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
    
    /* Init horisontal scroll for images */
    
    var $imgUL = $("#imgUL");
    var scrollWidth = prepareUL($imgUL, 'h');
    
    $("#imgLeft img").click(function(){
        $imgUL.scrollHorisontally(-1, scrollWidth);
    });
    
    $("#imgRight img").click(function(){
        $imgUL.scrollHorisontally(1, scrollWidth);
    });
	
	$imgUL.scrollHorisontally(0, 0);
	
	/* Rotate albums & images */
    
    $("#albUL img, #imgUL img").each(function(){
        return $(this).load(function(){
            var angle = parseInt(Math.random() * 50 - 25, 10);
            $(this).parent().removeClass('loadingdiv');
            $(this).css('transform', 'rotate(' + angle + 'deg)');
            return $(this);
        });
    });
});

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
	var src1_ = (direction === 'v') ? "icons/up_.png" : "icons/left_.png";
	var src2_ = (direction === 'v') ? "icons/down_.png" : "icons/right_.png";
    
    if (currentItem <= visibleLength - length) {
        $direction1.attr("src", src1_);
    }
    else {
        $direction1.attr("src", src1);
    }
	
    if (currentItem >= 0) {
        $direction2.attr("src", src2_);
    }
    else {
        $direction2.attr("src", src2);
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
