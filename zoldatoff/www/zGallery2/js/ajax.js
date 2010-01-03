/*
 * Title: JavaScript functions that manipulate DOM on client-side and interact with JSON data from server-side
 */

/*
 * Constant: AJAX_PATH
 * Path to PHP-files that get/send data from/to DB
 */
var AJAX_PATH = 'php/upload.php';

/*
 * Function: 
 * 
 * Adjusts several visual (CSS) parameters and interface behaviour (clicks and more).
 * 
 * See Also:
 * <refreshInterface>
 * <getCategories>
 * <fillTopImages>
 * <changeTopImage>
 * 
 */

$(document).ready(function(){
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

/*
 * Function:
 * Sets several CSS parameters basing on window size
 */
$(window).resize(refreshInterface);

/*
 * Function: fillTopImages
 * Shows the images in full-screen mode 
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


// Change image with fading
function changeTopImage(src){
    $('#imgTop').hide();
    $('#topImgDiv').addClass('loadingdiv');
    
    $('<img>').attr('src', src).load(function(){
        $('#topImgDiv').removeClass('loadingdiv').show();
        $('#imgTop').attr('src', src).fadeIn('slow');
        return false;
    });
}

// Set several CSS parameters basing on window size
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
	
    return false;
}

// Several AJAX requests
function getCategories(){
    $.getJSON(AJAX_PATH, {
        object: 'categories'
    }, fillCategories);
}

function getAlbums(category_id){
    $.getJSON(AJAX_PATH, {
        object: 'albums',
        category_id: category_id
    }, fillAlbums);
}

function getImages(album_id){
    $.getJSON(AJAX_PATH, {
        object: 'images',
        album_id: album_id
    }, fillImages);
}

// Generate list of categories
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
        });
        $("#navUL").append(myLi);
    }
    
    $("#navUL li:first-child").click();
}

// Generate list of albums
function fillAlbums(jsonData){
    var theList = jsonData.objectlist.album_list;
    var nItems = theList.length;
    var myLi, myImg, myDiv;
    
    $("#albUL").empty().css('top', '0');
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('albLI').addClass('loadingdiv');
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
        });
        $("#albUL").append(myLi);
    }
    
    initAlbumsScroll();
    
    $("#albUL li:first-child").click();
}

// Generate list of images
function fillImages(jsonData){
    var theList = jsonData.objectlist.image_list;
    var nItems = theList.length;
    var myLi;
    
    $("#imgUL").empty().css('left', '0');
    $('#imgTop').data('json', theList);
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('imgLI').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
        
        myImg = $('<img>').attr('src', theList[i].thumb_bw_src).attr('alt', theList[i].name);
        
        myLi.click(function(){
			// TODO: optimise here
            var jsonData = $(this).data('json');
            var n = $(this).data('n');
            var $imgMain = $('#imgMain');
            var $imgUL = $('#imgUL');
            
            $imgMain.toggleImage(jsonData.norm_src);
            $imgMain.data('json', jsonData).data('n', i);
            $('#imgTop').data('n', n);
            
            // Scroll the image list to center current image
            // TODO: Женькин метод
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

// Change th image if needed
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

// AJAX error callback function
function ajaxError(XMLHttpRequest, textStatus, errorThrown){
    //console.error(XMLHttpRequest);
    //console.error(textStatus);
    console.error(errorThrown);
    $('#status').stop().hide();
}

// AJAX complete callback function
function ajaxComplete(XMLHttpRequest, textStatus){
    $('#status').stop().hide();
}

// AJAX request send callback function
function ajaxSend(XMLHttpRequest){
    $('#status').show(1000);
}
