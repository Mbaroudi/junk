/**
 * @author appleapple
 */

 function superImage(imgSrc, loadingSrc, parentDiv){
 	this.mainImg = new Image();
	this.subImg = new Image();
	parentDiv.appendChild(this.mainImg);
	parentDiv.appendChild(this.subImg);
	
	function mainOnTop() {
		this.className = "img-show";
		this.nextSibling.className = "img-hide";
		this.parentNode.style.opacity = 1;
		this.parentNode.style.backgroundColor = "white";
	}
	
	function subOnTop(){
		this.previousSibling.className = "img-hide";
		this.className = "img-show";
	}
	
	this.subImg.src = loadingSrc;
	this.mainImg.src = imgSrc;
	
	this.subImg.onload = subOnTop;
	this.mainImg.onload = mainOnTop;
 }
 
 function getNumber(str) {
 	var pos_ = str.indexOf("_");
 	return str.substring(pos_+1, str.length);
 }
 
function onSubLoad() {
		document.getElementById("bottomDiv_" + getNumber(this.id)).appendChild(this);
		this.className = "img-show";
		
		if (this.height < this.parentNode.offsetHeight) {
			this.style.marginTop = Math.round((this.parentNode.offsetHeight - this.height) / 2) + 'px';
		}
		else
			this.style.marginTop = "0px";
}

function onMainLoad() {		
		document.getElementById("sub_" + getNumber(this.id)).className = "img-hide";
		document.getElementById("bottomDiv_" + getNumber(this.id)).appendChild(this);
		this.className = "img-show";
		
		if (this.height < this.parentNode.offsetHeight) {
				this.style.marginTop = Math.round((this.parentNode.offsetHeight - this.height) / 2) + 'px';
			}
		else
			this.style.marginTop = "0px";
			
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