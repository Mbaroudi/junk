/**
 * @author zoldatoff
 */

var ajaxPath = 'http://127.0.0.1/zgallery/php/upload.php';

$(document).ready(function(){
    $.ajaxSetup({
        url: ajaxPath,
        timeout: 10000,
        contentType: 'application/json',
        error: ajaxError,
        complete: ajaxComplete,
        beforeSend: ajaxSend
    });
    getCategories();
    $('header img').click(getCategories);
});

function getCategories(){
    $.getJSON(ajaxPath, {
        object: 'categories'
    }, fillCategories);
}

function getAlbums(category_id){
    $.getJSON(ajaxPath, {
        object: 'albums',
        category_id: category_id
    }, fillAlbums);
}

function getImages(album_id){
    $.getJSON(ajaxPath, {
        object: 'images',
        album_id: album_id
    }, fillImages);
}

function fillCategories(jsonData){
    var theList = jsonData.objectlist.category_list;
    var nItems = theList.length;
    var myLi;
    
    $("#navUL").empty();
    
    for (var i = 1; i < nItems; i++) {
        myLi = $('<li>').addClass('navLI').append(theList[i].name);
        myLi.data('json', theList[i]);
        myLi.click(function(){
            getAlbums($(this).data('json').category_id);
        });
        $("#navUL").append(myLi);
    }
}

function fillAlbums(jsonData){
    var theList = jsonData.objectlist.album_list;
    var nItems = theList.length;
    var myLi, myImg, myDiv;
    
    $("#albUL").empty();
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('albLI').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
		
		myImg = $('<img>').attr('src', theList[i].image.thumb_src).attr('alt',theList[i].image.name);
		myDiv = $('<div>').addClass('albTitle').append(theList[i].name);

		myLi.append(myImg).append(myDiv);
		
        myLi.click(function(){
			var $albUL = $('#albUL');
            getImages($(this).data('json').album_id);
			
			// Scroll the albums list to center current album
			var steps =  Math.round($albUL.data('visibleLength')/2) - $albUL.data('currentItem') - $(this).data('n');
			$albUL.scrollVertically(steps, $albUL.data('scrollDelta'));
			
			$('#albUL img').removeClass('active');
			$(this).children('img').addClass('active');
        });
        $("#albUL").append(myLi);
    }
	
	initAlbumsScroll();
}

function fillImages(jsonData){
	var theList = jsonData.objectlist.image_list;
    var nItems = theList.length;
    var myLi;
    
    $("#imgUL").empty();
    
    for (var i = 1; i < nItems; i++) {
        myLi = $('<li>').addClass('imgLI').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
		
		myImg = $('<img>').attr('src', theList[i].thumb_src).attr('alt',theList[i].name);
		
        myLi.click(function(){
			var jsonData = $(this).data('json');
			var $imgMain = $('#imgMain');
			var $imgUL = $('#imgUL');
			
			$imgMain.toggleImage(jsonData.norm_src);
			$imgMain.data('json', jsonData).data('n', i);
			
			// Scroll the image list to center current image
			var steps = Math.round($imgUL.data('visibleLength')/2) - $imgUL.data('currentItem') - $(this).data('n');
			$imgUL.scrollHorisontally(steps, $imgUL.data('scrollDelta'));
			
			$('#imgUL img').removeClass('active');
			$(this).children('img').addClass('active');
        });
		
		myLi.append(myImg);
        $("#imgUL").append(myLi);
    }
	
	initImagesScroll();
}

$.fn.toggleImage = function(newSrc, duration) {
	var d = duration ? duration : 500;
	
	$(this).parent().addClass('loadingdiv');
	$(this).fadeOut(d, function(){
		$(this).attr('src', newSrc).fadeIn(d);
		$(this).parent().removeClass('loadingdiv');
	});
}

function ajaxError(XMLHttpRequest, textStatus, errorThrown){
    //console.info(XMLHttpRequest);
    //console.info(textStatus);
    //console.info(errorThrown);
    $('header img').attr('src', 'icons/main_.png');
}

function ajaxComplete(XMLHttpRequest, textStatus){
    $('header img').attr('src', 'icons/main_.png');
}

function ajaxSend(XMLHttpRequest){
    $('header img').attr('src', 'css/loader.gif');
}
