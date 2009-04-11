/**
 * @author Zoldatoff
 */
 
 function getNumber(str) {
 	var pos_ = str.indexOf("_");
 	return str.substring(pos_+1, str.length);
 }
 
 function placeImage(theImg) {
 		with (theImg) {
			var parentH = parentNode.offsetHeight;
			if (height < parentH) 
				style.marginTop = Math.round((parentH - height) / 2) + 'px';
			else 
				style.marginTop = "0px";
		}
 }
 
function onSubLoad() {
		document.getElementById("bottomDiv_" + getNumber(this.id)).appendChild(this);
		this.className = "img-show";
		placeImage(this);
}

function onMainLoad() {		
		document.getElementById("sub_" + getNumber(this.id)).className = "img-hide";
		document.getElementById("bottomDiv_" + getNumber(this.id)).appendChild(this);
		
		this.className = "img-show";
		placeImage(this);
		
		this.onclick = function() { document.getElementById("mainImage").src = this.src; }
}
 
 function myImage(imgSrc, loadingSrc, imgNum){
 	this.mainImg = new Image();
	this.subImg = new Image();
	
	this.subImg.src = loadingSrc;
	this.mainImg.src = imgSrc;
	
	this.mainImg.id = "main_" + imgNum;
	this.subImg.id = "sub_" + imgNum;
		
	this.subImg.onload = onSubLoad;
	this.mainImg.onload = onMainLoad;
}