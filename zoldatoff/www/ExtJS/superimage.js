/**
 * @author Zoldatoff zoldatoff@gmail.com
 */
var bottomNum = 12;

/* Функция отделяет 4-значный номер в конце идентификатора */
function getNumber(str){
    var pos_ = str.indexOf("_");
    return str.substring(pos_ + 1, str.length);
}

/* Функция позиционирует рисунок по высоте внутри родительского div-а */
function placeImage(theImg){
    with (theImg) {
        var parentH = parentNode.offsetHeight; // - 2*parseInt(parentNode.style.padding);
        if (height < parentH) 
            style.marginTop = (parentH - height) / 2 + 'px';
        else 
            style.marginTop = "0px";
    }
}

/* 
 * При загрузке маленького изображения, оно назначается дочерним
 * div-у с соответствующим id и позиционируется
 */
function onSubLoad(){
    if (this.parentNode != document.getElementById("bottomDiv_" + getNumber(this.id))) 
        document.getElementById("bottomDiv_" + getNumber(this.id)).appendChild(this);
    placeImage(this);
    this.className = "img-show";
}

/* 
 * При загрузке основного изображения
 * 1. Убираем с экрана рисунок с процессом загрузки
 * 2. Добавляем и позиционируем основное изображение
 * 3. Добавляем обработчики событий
 */
function onMainLoad(){
    var parentDiv = document.getElementById("bottomDiv_" + getNumber(this.id))
    
    document.getElementById("sub_" + getNumber(this.id)).className = "img-hide";
    parentDiv.appendChild(this);
    parentDiv.style.opacity = "0.5";
    
    this.className = "img-show";
    placeImage(this);
    
    this.onclick = function(){
        document.getElementById("mainImage").src = this.src;
        //msg('Click!', 'You have selected the image {0}', this.src)
    }
    parentDiv.onmouseover = function(){
        this.style.opacity = "1";
    }
    parentDiv.onmouseout = function(){
        this.style.opacity = "0.4";
    }
}

/*
 * Класс, объединяющий изображение с процессом загрузки и основное изображение
 */
function theImage(imgSrc, loadingSrc, imgNum){

	if (!document.getElementById("bottomDiv_" + imgNum)) {
		this.bottomSubDiv = document.createElement("div");
		this.bottomSubDiv.id = "bottomDiv_" + imgNum;
		this.bottomSubDiv.className = "thumbDiv";
		this.bottomSubDiv.style.opacity = "1";
		//this.bottomSubDiv.style.width = document.getElementById("bottomDiv").offsetWidth / bottomNum - thumbDivPadding - bottomNum + 'px';
		document.getElementById("south").appendChild(this.bottomSubDiv);
	}
	else
		this.bottomSubDiv = document.getElementById("bottomDiv_" + imgNum);
    
    /*--------------------------------*/
    
    if (!document.getElementById("sub_" + imgNum)) {
        this.subImg = new Image();
        this.subImg.id = "sub_" + imgNum;
        this.subImg.onload = onSubLoad;
    }
    else 
        this.subImg = document.getElementById("sub_" + imgNum);
    
    this.subImg.className = "img-show";
    this.subImg.src = loadingSrc;
    
    /*--------------------------------*/
    
    if (!document.getElementById("main_" + imgNum)) {
        this.mainImg = new Image();
        this.mainImg.id = "main_" + imgNum;
        this.mainImg.onload = onMainLoad;
		this.mainImg.onerror = function() {this.src = "img/loader_4_fff.gif"}
    }
    else 
        this.mainImg = document.getElementById("main_" + imgNum);
    
    this.mainImg.className = "img-hide";
    this.mainImg.src = imgSrc;
}
