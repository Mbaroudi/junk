/**
 * @author Zoldatoff
 */

function onImgLoad () {
	with (this) {
		style.maxHeight = "100%";
		style.maxWidth = "100%";
		style.verticalAlign = "middle";
		/*
		if (height < parentNode.offsetHeight) {
			style.marginTop = Math.round((parentNode.offsetHeight - height) / 2) + 'px';
		}
		else {
			style.marginTop = "0px";
		}*/
	}
}

function wwwImage(imgSrc, parentDiv) {
	this.theImg = new Image();
	parentDiv.appendChild(this.theImg);
	//this.theImg.src = imgSrc;
	//theDiv = parentDiv;
	this.theImg.onload = onImgLoad;
	
	this.changeSrc = function(newSrc) {
		this.theImg.src = newSrc;
		this.theImg.onImgLoad;
	}
	
	this.preload = function(waitSrc){
		var tmpImg = new Image();
		this.theImg.src = waitSrc;
		tmpImg.src = imgSrc;
		tmpImg.onload = this.changeSrc(imgSrc);
	}
	
	this.preload("img/loader1.gif");
}