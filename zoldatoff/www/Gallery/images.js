/**
 * @author Zoldatoff
 */

function onImgLoad () {
	with (this) {
		style.maxHeight = "100%";
		style.maxWidth = "100%";
		
		if (height < parentNode.offsetHeight) {
			style.marginTop = Math.round((parentNode.offsetHeight - height) / 2) + 'px';
		}
		else {
			style.marginTop = "0px";
		}
		
		/*
		if (width > parentNode.offsetWidth && height > parentNode.offsetHeight)
		//картинка ваще не поместилась
		{
			if (width / parentNode.offsetWidth > height / parentNode.offsetHeight) {
				style.width = "100%";
				style.height = "auto";
				style.marginTop = Math.round((parentNode.offsetHeight - height) / 2) + 'px';
			}
			else {
				style.height = "auto";
				style.width = "100%";
				style.marginTop = "0px";
			}
		}
		else if (height > parentNode.offsetHeight)
		//картинка не поместилась по высоте
		{
			style.width = "auto";
			style.height = "100%";
			style.marginTop = "0px";
		}
		else if (width > parentNode.offsetWidth)
		//картинка не поместилась по ширине 
		{
			style.width = "100%";
			style.height = "auto";
			style.marginTop = Math.round( (parentNode.offsetHeight - height) / 2 ) + 'px';
		}
		else 
		{
			style.width = width + "px";
			style.height = height + "px";
			style.marginTop = Math.round( (parentNode.offsetHeight - height) / 2 ) + 'px';
		}
		*/
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