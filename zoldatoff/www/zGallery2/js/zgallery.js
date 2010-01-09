/* *********************************************************************
 * Title: zGallery JS
 * JavaScript functions that manipulate DOM on client-side and interact with JSON data from server-side
 * *********************************************************************/

/* *********************************************************************
 * Constant: AJAX_PATH
 * Path to PHP-files that get/send JSON data from/to DB
 * 
 * Constant: USE_CUFON
 * Wether to use Cufon for rendering fonts or not
 */
var AJAX_PATH = 'php/upload.php';
var USE_CUFON = true;



/* *********************************************************************
 * Namespace: jQuery
 * 
 * Group: Main callback functions
 * Functions running on document.ready & window.resize events
 * *********************************************************************/

/* *********************************************************************
 * Function: jQuery.document.ready
 * Adjusts several visual (CSS) parameters and interface behaviour (clicks and more).
 * 
 * See Also: 
 * 		<refreshInterface> 		
 */
$(document).ready(function(){
	if ($.browser.safari) {
		USE_CUFON = false;
	}
	
	if (USE_CUFON) {
		Cufon.replace('h1', {
			fontFamily: 'Waltograph'
		});
	}
	
	// Disable right click
    $(document).bind("contextmenu", function(e){
        return false;
    });
	
	// Adjust AJAX parameters
    $.ajaxSetup({
        url: AJAX_PATH,
        timeout: 10000,
        contentType: 'application/json',
        error: ajaxError,
        complete: ajaxComplete,
        beforeSend: ajaxSend
    });
    
	// Set several CSS parameters basing on window size
    refreshInterface();
    
	// Request categories list
    getCategories();
    $('#logo').click(getCategories);
    
	// Bind actions to controls (left/right etc.)
	
    $('#toLeft img').click(function(){
        var n = $('#imgUL img.active').parent().data('n');
        $('#imgUL li:eq(' + (n - 1) + ')').click();
        return false;
    });
    
    $('#toRight img').click(function(){
        var n = $('#imgUL img.active').parent().data('n');
        $('#imgUL li:eq(' + (n + 1) + ')').click();
        return false;
    });
    
    $('#topLeft img').click(function(){
        fillTopImages(-1);
        return false;
    });
    
    $('#topRight img').click(function(){
        fillTopImages(1);
        return false;
    });
    
    $('#imgMain').click(function(){
        $('#topDiv').show();
        var src = $(this).data('json').full_src;
		
        changeTopImage(src);
        fillTopImages(0);
        
        return false;
    });
    
    $('#topImgDiv').click(function(){
        $('#topDiv').fadeOut('slow');
        return false;
    });
});

/* *********************************************************************
 * Function: jQuery.window.resize
 * Sets several CSS parameters basing on window size
 * 
 * See Also: 
 * 		<refreshInterface> 	
 */
$(window).resize(refreshInterface);



/* *********************************************************************
 * Group: jQuery extensions
 * jQuery extensions for DOM manipulation
 * *********************************************************************/

/* *********************************************************************
 * Function: jQuery.toggleImage
 * Changes the image source path with fading effect and loading icon.
 * 
 * Parameters:
 * 		newSrc - New image source path
 * 		duration - Effect duration (default: 500ms) 
 * 
 * Returns: 
 * 		jQuery object
 */
$.fn.toggleImage = function(newSrc, duration){
    var d = duration ? duration : 500;
    var $t = $(this);
    
    if ($t.attr('src') != newSrc) {
        $t.parent().addClass('loadingdiv');
        $t.fadeOut(d, function(){
            $t.attr('src', newSrc);
            $t.load(function(){
                $t.parent().removeClass('loadingdiv');
                $t.fadeIn(d);
            });
        });
    }
    return $t;
};

/* *********************************************************************
 * Function: jQuery.prepareUL
 * Determines scrolling parameters for UL element and stores them in jQuery.data() attributes
 * 
 * Parameters:
 * 		direction - scrolling direction: 'v' - vertical, 'h' - horisontal
 * 
 * Returns: 
 * 		jQuery object
 */
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

/* *********************************************************************
 * Function: jQuery.fullHeight
 * Determines the height of an element including margins
 * 
 * Returns: 
 * 		jQuery object
 */
$.fn.fullHeight = function(){
    return parseInt($(this).outerHeight(), 10) +
    parseInt($(this).css("margin-top"), 10) +
    parseInt($(this).css("margin-bottom"), 10);
};

/* *********************************************************************
 * Function: jQuery.fullWidth
 * Determines the width of an element including margins
 * 
 * Returns: 
 * 		jQuery object
 */
$.fn.fullWidth = function(){
    return parseInt($(this).outerWidth(), 10) +
    parseInt($(this).css("margin-left"), 10) +
    parseInt($(this).css("margin-right"), 10);
};

/* *********************************************************************
 * Function: jQuery.scroll
 * Scrolls the UL element in selected direction
 * 
 * Parameters:
 * 		steps - number of steps to scroll (can be zero or negative)
 * 		scrollSize - size of scrolling step (in pixels)
 * 		direction - scrolling direction: 'v' - vertical, 'h' - horisontal
 * 
 * Returns: 
 * 		jQuery object
 */
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

/* *********************************************************************
 * Function: jQuery.scrollVertically
 * Scrolls the UL element vertically
 * 
 * Parameters:
 * 		steps - number of steps to scroll (can be zero or negative)
 * 		scrollHeight - size of scrolling step (in pixels)
 * 
 * Returns: 
 * 		jQuery object
 */
$.fn.scrollVertically = function(steps, scrollHeight){
	var $t = $(this).scroll(steps, scrollHeight, 'v');
	return changeIcon($t, 'v', $('#albUp img'), $("#albDown img"));
};

/* *********************************************************************
 * Function: jQuery.scrollHorisontally
 * Scrolls the UL element horisontally
 * 
 * Parameters:
 * 		steps - number of steps to scroll (can be zero or negative)
 * 		scrollHeight - size of scrolling step (in pixels)
 * 
 * Returns: 
 * 		jQuery object
 */
$.fn.scrollHorisontally = function(steps, scrollWidth){
    var $t = $(this).scroll(steps, scrollWidth, 'h');
	return changeIcon($t, 'h', $('#imgLeft img'), $("#imgRight img"));
};


/* *********************************************************************
 * Namespace: zGallery
 * 
 * Group: AJAX calls
 * Functions that send AJAX requests and react on success/failure
 * *********************************************************************/

/* *********************************************************************
 * Function: getCategories
 * Sends an AJAX request for list of categories
 * 
 * See Also:
 * 		<fillCategories>
 */
function getCategories(){
    $.getJSON(AJAX_PATH, {
        object: 'categories'
    }, fillCategories);
}

/* *********************************************************************
 * Function: getAlbums
 * Sends an AJAX request for list of albums
 * 
 * See Also:
 * 		<fillAlbums>
 */
function getAlbums(category_id){
    $.getJSON(AJAX_PATH, {
        object: 'albums',
        category_id: category_id
    }, fillAlbums);
}

/* *********************************************************************
 * Function: getImages
 * Sends an AJAX request for list of images
 * 
 * See Also:
 * 		<fillImages>
 */
function getImages(album_id){
    $.getJSON(AJAX_PATH, {
        object: 'images',
        album_id: album_id
    }, fillImages);
}



/* *********************************************************************
 * Group: AJAX callbacks
 * Functions that react on success/failure AJAX requests
 * *********************************************************************/

/* *********************************************************************
 * Function: ajaxError
 * Callback function for AJAX "request error" event.
 */
function ajaxError(XMLHttpRequest, textStatus, errorThrown){
    //console.error(XMLHttpRequest);
    //console.error(textStatus);
    console.error(errorThrown);
    $('#status').stop().hide();
}

/* *********************************************************************
 * Function: ajaxComplete
 * Callback function for AJAX "complete request" event.
 */
function ajaxComplete(XMLHttpRequest, textStatus){
    $('#status').stop().hide();
}

/* *********************************************************************
 * Function: ajaxSend
 * Callback function for AJAX "send request" event.
 */
function ajaxSend(XMLHttpRequest){
    $('#status').show(1000);
}



/* *********************************************************************
 * Group: DOM manipulations
 * Main JS function that fill UL elements with images and bind events to them
 * *********************************************************************/

/* *********************************************************************
 * Function: fillCategories
 * Fills the #navUL element with the list of categories. Binds *onclick* events to the list.
 * 
 * Parameters:
 * 		jsonData - Data from server-side in JSON format with categories information
 * 
 * See Also:
 * 		<getCategories>
 */
function fillCategories(jsonData){
    var theList = jsonData.objectlist.category_list;
    var nItems = theList.length;
    var myLi;
    
    $('#navUL').empty();
    
    for (var i = 1; i < nItems; i++) {
        myLi = $('<li>').addClass('navLI').append(theList[i].name);
        myLi.data('json', theList[i]);
        myLi.click(function(){
            getAlbums($(this).data('json').category_id);
            $('#navUL li').removeClass('active');
            $(this).addClass('active');
			if (USE_CUFON) {
				Cufon.refresh('#navUL');
			}
        });
        $("#navUL").append(myLi);
    }
    
	if (USE_CUFON) {
		Cufon.replace('#navUL', {
			fontFamily: 'Sharpie Marker'
		});
	}
    $("#navUL li:first-child").click();
}

/* *********************************************************************
 * Function: fillAlbums
 * Fills the #albUL element with the list of albums. Binds *onclick* events to the list.
 * 
 * Parameters:
 * 		jsonData - Data from server-side in JSON format with albums information
 * 
 * See Also:
 * 		<getAlbums>
 */
function fillAlbums(jsonData){
    var theList = jsonData.objectlist.album_list;
    var nItems = theList.length;
    var myLi, myImg, myDiv;
    
    $("#albUL").empty().css('top', '0');
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
        
        myImg = $('<img>').attr('src', theList[i].image.thumb_bw_src).attr('alt', theList[i].image.name);
        myDiv = $('<div>').addClass('albTitle').append(theList[i].name);
        
        myLi.append(myImg).append(myDiv);
        
        myLi.click(function(){
            var $albUL = $('#albUL');
            var jsonData = $(this).data('json');
            getImages(jsonData.album_id);
            
            // Scroll the albums list to center current album
            //var steps =  Math.floor($albUL.data('visibleLength')/2) - $albUL.data('currentItem') - $(this).data('n');
            //$albUL.scrollVertically(steps, $albUL.data('scrollDelta'));
            
            // Change the visual of selected item
            $albUL.children().each(function(){
                var jsonData = $(this).data('json');
                $(this).children('img').removeClass('active').attr('src', jsonData.image.thumb_bw_src);
            });
            $(this).children('img').addClass('active').attr('src', jsonData.image.thumb_src);
            
            $("#albUL li").removeClass('active');
            $(this).addClass('active');
			if (USE_CUFON) {
				Cufon.refresh('.albTitle');
			}
        });
        $("#albUL").append(myLi);
    }
    
    initAlbumsScroll();
    if (USE_CUFON) {
		Cufon.replace('.albTitle', {
			fontFamily: 'Sharpie Marker'
		});
	}
    $("#albUL li:first-child").click();
}

/* *********************************************************************
 * Function: fillImages
 * Fills the #imgUL element with the list of images. Binds *onclick* events to the list.
 * 
 * Parameters:
 * 		jsonData - Data from server-side in JSON format with images information
 * 
 * See Also:
 * 		<getImages>
 */
function fillImages(jsonData){
    var theList = jsonData.objectlist.image_list;
    var nItems = theList.length;
    var myLi;
    
    $("#imgUL").empty().css('left', '0');
    $('#imgTop').data('json', theList);
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
        
        myImg = $('<img>').attr('src', theList[i].thumb_bw_src).attr('alt', theList[i].name);
        
        myLi.click(function(){
            var jsonData = $(this).data('json');
            var n = $(this).data('n');
            var $imgMain = $('#imgMain');
            var $imgUL = $('#imgUL');
            
            $imgMain.toggleImage(jsonData.norm_src);
            $imgMain.data('json', jsonData).data('n', i);
            $('#imgTop').data('n', n);
            
            // Scroll the image list to center current image
            var steps = Math.floor($imgUL.data('visibleLength') / 2) - $imgUL.data('currentItem') - n;
            $imgUL.scrollHorisontally(steps, $imgUL.data('scrollDelta'));
            
            // Change the visual of selected item
            $imgUL.children().each(function(){
                var jsonData = $(this).data('json');
                $(this).children('img').removeClass('active').attr('src', jsonData.thumb_bw_src);
            });
            $(this).children('img').addClass('active').attr('src', jsonData.thumb_src);
            
            $("#imgUL li").removeClass('active');
            $(this).addClass('active');
            
            if (jsonData.name) {
                $('#imgInfo').text(jsonData.name);
            }
            else {
                $('#imgInfo').text(' ');
            }
        });
        
        myLi.append(myImg);
        $("#imgUL").append(myLi);
    }
    
    initImagesScroll();
    
    var tmp = Math.min(nItems, 4);
    $('#imgUL li:nth-child(' + tmp + ')').click();
}



/* *********************************************************************
 * Group: Auxiliary functions
 * Some repeating code was placed into these functions
 * *********************************************************************/

/* *********************************************************************
 * Function: refreshInterface
 * Sets several CSS parameters basing on window size
 */
function refreshInterface(){
    var $imgDiv = $('#imgDiv');
    var h = $imgDiv.height();
    $imgDiv.css('line-height', h + 'px');
    
    h = $('body').height() - 40;
    $('#topImgDiv').css('line-height', h + 'px');
    
    var $albList = $('#albList');
    $albList.height('100%');
    h = $albList.height() - 60;
    var H = Math.floor(h / 110) * 110;
    $albList.height(H).css('margin-top', '-' + (H / 2) + 'px');
    
    $('#albUL').css('top', '0').prepareUL('v');
    $('#albUL img.active').parent().click();
}

/* *********************************************************************
 * Function: initAlbumsScroll
 * Initializes albums list: binds click&load events, determines scrolling parameters
 */
function initAlbumsScroll(){
	/* Init vertical scroll for albums */
	var $albUL = $("#albUL").prepareUL('v');
    var scrollHeight = $albUL.data('scrollDelta');
	
	$("#albUp img").unbind('click').click(function(){
        $albUL.scrollVertically(1, scrollHeight);
    });
    
    $("#albDown img").unbind('click').click(function(){
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

/* *********************************************************************
 * Function: initImagesScroll
 * Initializes images list: binds click&load events, determines scrolling parameters
 */
function initImagesScroll(){
	// Init horisontal scroll for images
	var $imgUL = $('#imgUL').prepareUL('h');
    var scrollWidth = $imgUL.data('scrollDelta');
	
	$('#imgLeft img').unbind('click').click(function(){
        $imgUL.scrollHorisontally(1, scrollWidth);
    });
	
	$('#imgRight img').unbind('click').click(function(){
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

/* *********************************************************************
 * Function: changeIcon
 * Determines wether to hide or show scrolling icons
 * 
 * Parameters:
 * 		$ul - jQuery object for UL element
 * 		direction - scrolling direction: 'v' - vertical, 'h' - horisontal
 * 		$direction1 - jQuery object for left/up arrow
 * 		$direction2 - jQuery object for right/down arrow
 */
function changeIcon($ul, direction, $direction1, $direction2) {
	var length = $ul.data('length');
    var visibleLength = $ul.data('visibleLength');
    var currentItem = $ul.data('currentItem');
	
	var src1 = (direction === 'v') ? 'icons/up.png' : 'icons/left.png';
	var src2 = (direction === 'v') ? 'icons/down.png' : 'icons/right.png';
	
	var d = (direction === 'v') ? 3 : 4;
    
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

/* *********************************************************************
 * Function: fillTopImages
 * Shows the images in full-screen mode 
 * 
 * Parameters:
 * 		step - Show the image that is several *steps* from the current
 */
function fillTopImages(step) {
	var $imgTop = $('#imgTop');
	var $imgTopRight = $('#topRight img');
	var $imgTopLeft = $('#topLeft img');
	
	var n = $imgTop.data('n');
    var jsonData = $imgTop.data('json');
    
    if (step!==0 && jsonData[n + step]) {
        var src = jsonData[n + step].full_src;
        $imgTop.data('n', n + step);
        changeTopImage(src);
    }
    
    if (jsonData[n + step + 1]) {
        var src_ = jsonData[n + step + 1].thumb_src;
        $imgTopRight.attr('src', src_).show();
    }
	else {
		$imgTopRight.hide();
	}
	
	if (jsonData[n + step - 1]) {
        var _src = jsonData[n + step - 1].thumb_src;
        $imgTopLeft.attr('src', _src).show();
    }
	else {
		$imgTopLeft.hide();
	}
}

/* *********************************************************************
 * Function: changeTopImage
 * Changes image source path with fading
 * 
 * Parameters:
 * 		src - String with new image *source* path
 */
function changeTopImage(src){
    $('#imgTop').hide();
    $('#topImgDiv').addClass('loadingdiv');
    
    $('<img>').attr('src', src).load(function(){
        $('#topImgDiv').removeClass('loadingdiv').show();
        $('#imgTop').attr('src', src).fadeIn('slow');
        return false;
    });
}