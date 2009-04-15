/**
 * @author Zoldatoff
 */
 
 function getNumber(str) {
 	var pos_ = str.indexOf("_");
 	return str.substring(pos_+1, str.length);
 }
 
 function placeImage(theImg) {
 		with (theImg) {
			var parentH = parentNode.offsetHeight - 2*parseInt(parentNode.style.padding);
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
		var parentDiv = document.getElementById("bottomDiv_" + getNumber(this.id) )

		document.getElementById("sub_" + getNumber(this.id)).className = "img-hide";
		parentDiv.appendChild(this);
		parentDiv.style.opacity = "0.5";
		
		this.className = "img-show";
		placeImage(this);
		
		this.onclick = function() { document.getElementById("mainImage").src = this.src; }
		parentDiv.onmouseover = function(){this.style.opacity = "1"; }
		parentDiv.onmouseout = function(){this.style.opacity = "0.4"; }
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