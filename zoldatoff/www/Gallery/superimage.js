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
