/**
 * @author zoldatoff
 */

var ajaxPath = 'php/upload.php';

$(document).ready(function(){
    $.ajaxSetup({
        url: ajaxPath,
        timeout: 10000,
        contentType: 'application/json',
        error: ajaxError,
        complete: ajaxComplete,
        beforeSend: ajaxSend
    });
	
	refreshInterface();
    
	getCategories();
    $('#logo').click(getCategories);
	
	$('#toLeft img').click(function(){
		var n = $('#imgUL img.active').parent().data('n');
		$('#imgUL li:eq('+(n-1)+')').click();
	});
	
	$('#toRight img').click(function(){
		var n = $('#imgUL img.active').parent().data('n');
		$('#imgUL li:eq('+(n+1)+')').click();
	});
});

$(window).resize(refreshInterface);

function refreshInterface() {
	var $imgDiv = $('#imgDiv');
	var h = $imgDiv.height();
	$imgDiv.css('line-height', h + 'px');
	
	var $albList = $('#albList');
	$albList.height('100%');
	h = $albList.height() - 60;
	var H = Math.floor(h/110)*110;
	$albList.height(H).css('margin-top', '-' + (H/2) + 'px');
	
	$('#albUL').css('top', '0').prepareUL('v');
	$('#albUL img.active').parent().click();
}

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
    
    $('#navUL').empty();
    
    for (var i = 1; i < nItems; i++) {
        myLi = $('<li>').addClass('navLI').append(theList[i].name);
        myLi.data('json', theList[i]);
        myLi.click(function(){
            getAlbums($(this).data('json').category_id);
        });
        $("#navUL").append(myLi);
    }
	
	$("#navUL li:first-child").click();
}

function fillAlbums(jsonData){
    var theList = jsonData.objectlist.album_list;
    var nItems = theList.length;
    var myLi, myImg, myDiv;
    
    $("#albUL").empty().css('top', '0');
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('albLI').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
		
		myImg = $('<img>').attr('src', theList[i].image.thumb_bw_src).attr('alt',theList[i].image.name);
		myDiv = $('<div>').addClass('albTitle').append(theList[i].name);

		myLi.append(myImg).append(myDiv);
		
        myLi.click(function(){
			var $albUL = $('#albUL');
			var jsonData = $(this).data('json');
            getImages(jsonData.album_id);
			
			// Scroll the albums list to center current album
			var steps =  Math.floor($albUL.data('visibleLength')/2) - $albUL.data('currentItem') - $(this).data('n');
			$albUL.scrollVertically(steps, $albUL.data('scrollDelta'));
			
			// Change the visual of selected item
			$albUL.children().each(function(){
				var jsonData = $(this).data('json');
				$(this).children('img').removeClass('active').attr('src', jsonData.image.thumb_bw_src);
			});
			$(this).children('img').addClass('active').attr('src', jsonData.image.thumb_src);
        });
        $("#albUL").append(myLi);
    }
	
	initAlbumsScroll();
	$("#albUL li:first-child").click();
}

function fillImages(jsonData){
	var theList = jsonData.objectlist.image_list;
    var nItems = theList.length;
    var myLi;
    
    $("#imgUL").empty().css('left', '0');
    
    for (var i = 0; i < nItems; i++) {
        myLi = $('<li>').addClass('imgLI').addClass('loadingdiv');
        myLi.data('json', theList[i]).data('n', i);
		
		myImg = $('<img>').attr('src', theList[i].thumb_bw_src).attr('alt',theList[i].name);
		
        myLi.click(function(){
			var jsonData = $(this).data('json');
			var $imgMain = $('#imgMain');
			var $imgUL = $('#imgUL');
			
			$imgMain.toggleImage(jsonData.norm_src);
			$imgMain.data('json', jsonData).data('n', i);
			
			// Scroll the image list to center current image
			// TODO: Album with 2 images
			var steps = Math.floor($imgUL.data('visibleLength')/2) - $imgUL.data('currentItem') - $(this).data('n');
			$imgUL.scrollHorisontally(steps, $imgUL.data('scrollDelta'));
			
			// Change the visual of selected item
			$imgUL.children().each(function(){
				var jsonData = $(this).data('json');
				$(this).children('img').removeClass('active').attr('src', jsonData.thumb_bw_src);
			});
			$(this).children('img').addClass('active').attr('src', jsonData.thumb_src);
        });
		
		myLi.append(myImg);
        $("#imgUL").append(myLi);
    }
	
	initImagesScroll();
	
	var tmp = Math.min(nItems, 4); 
	$('#imgUL li:nth-child(' + tmp + ')').click();
}

$.fn.toggleImage = function(newSrc, duration) {
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

function ajaxError(XMLHttpRequest, textStatus, errorThrown){
    //console.info(XMLHttpRequest);
    //console.info(textStatus);
    console.info(errorThrown);
    $('#status').stop().hide();
}

function ajaxComplete(XMLHttpRequest, textStatus){
    $('#status').stop().hide();
}

function ajaxSend(XMLHttpRequest){
    $('#status').show(1000);
}
