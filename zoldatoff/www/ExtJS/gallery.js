/**
 * @author dsoldatov
 */

 function loadAlbum(albumName) {
 	if (!albumName) albumName = "squirell";
	
 	// Заполняем нижний div
	var theBottomSrc = new Array(5);
	var theBottomImg = new Array(5);
	
	for (var i = 0; i < bottomNum; i++) {
		theBottomSrc[i] = albumName + "/0" + (1 + i % 5) + ".jpg"
		theBottomImg[i] = new theImage(theBottomSrc[i], "img/loader_2_fff.gif", "000" + (i + 1));
	}
 }
