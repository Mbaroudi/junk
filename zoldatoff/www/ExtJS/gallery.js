/**
 * @author dsoldatov
 */
function loadAlbum(albumName){
    if (!albumName) 
        albumName = "squirell";
    
    // Заполняем нижний div
    var theBottomSrc = new Array(5);
    var theBottomImg = new Array(5);
    
    for (var i = 0; i < bottomNum; i++) {
        theBottomSrc[i] = albumName + "/0" + (1 + i % 5) + ".jpg"
        theBottomImg[i] = new theImage(theBottomSrc[i], "img/loader_2_fff.gif", "000" + (i + 1));
    }
	
	reposition();
}

function moveLeft(){
    var theDiv = document.getElementById("bottomDiv_0001");
    theDiv.style.left = theDiv.offsetLeft - theDiv.offsetWidth + 'px';
    //theDiv.style.position = "absolute";
    
    for (var i = 1; i < bottomNum; i++) {
        var theDiv = document.getElementById("bottomDiv_000" + (i + 1));
        var thePrevDiv = document.getElementById("bottomDiv_000" + i);
        theDiv.style.left = thePrevDiv.offsetLeft + thePrevDiv.offsetWidth + 'px';
        theDiv.style.position = "absolute";
    }
}

function moveRight(){
    var theDiv = document.getElementById("bottomDiv_0001");
    theDiv.style.left = theDiv.offsetLeft + theDiv.offsetWidth + 'px';
    //theDiv.style.position = "absolute";
    
    for (var i = 1; i < bottomNum; i++) {
        var theDiv = document.getElementById("bottomDiv_000" + (i + 1));
        var thePrevDiv = document.getElementById("bottomDiv_000" + i);
        theDiv.style.left = thePrevDiv.offsetLeft + thePrevDiv.offsetWidth + 'px';
        theDiv.style.position = "absolute";
    }
}

function reposition(){
    for (var i = 0; i < bottomNum; i++) {
        var theDiv = document.getElementById("bottomDiv_000" + (i + 1));
        theDiv.style.position = "relative";
		theDiv.style.left = null;
    }
}
