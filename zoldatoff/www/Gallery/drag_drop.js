/**
 * @author Zoldatoff
 */

var moveState = false;
// Переменные координат мыши в начале перемещения, пока неизвестны
var x0, y0;
// Начальные координаты элемента, пока неизвестны
var divX0, divY0;

var dragElement;
var dragDirection;

// Объявим функцию для определения координат мыши
function defPosition(event) {
    var x = y = 0;
    if (document.attachEvent != null) { // Internet Explorer & Opera
        x = window.event.clientX + document.documentElement.scrollLeft + document.body.scrollLeft;
        y = window.event.clientY + document.documentElement.scrollTop + document.body.scrollTop;
    }
    if (!document.attachEvent && document.addEventListener) { // Gecko
        x = event.clientX + window.scrollX;
        y = event.clientY + window.scrollY;
    }
    return {x:x, y:y};
}

// Функция инициализации движения
// Записываем всё параметры начального состояния
function initMove(event) {
    var event = event || window.event;
	dragElement = event.target || ev.srcElement;
	
	if (dragElement.id == 'dragDiv' || dragElement.id == "horizontal2") {
		dragDirection = 'h';
		x0 = defPosition(event).x;
		y0 = defPosition(event).y;
		divX0 = dragElement.offsetLeft; //style.left
		divY0 = dragElement.offsetTop; //style.top
		moveState = true;
	}
	else 
		dragElement = null;
}

// И последнее
// Функция обработки движения:
function moveHandler(event) {
    var event = event || window.event;
    if (moveState &&
		divX0 + defPosition(event).x - x0 > 50 &&
		divX0 + defPosition(event).x - x0 < document.body.clientWidth - 50 &&
		dragElement.id == 'dragDiv')
	{
        dragElement.style.left = divX0 + defPosition(event).x - x0 + 'px';	
        
		document.getElementById("leftDiv").style.width = dragElement.style.left;
		document.getElementById("mainDiv").style.left = dragElement.style.left;
		document.getElementById("mainDiv").style.width =
			document.body.clientWidth - 
			document.getElementById("leftDiv").clientWidth - 
			dragElement.clientWidth + 'px';
    }
	
	if (moveState &&
		dragElement.id == "horizontal2")
	{
		dragElement.style.top = divY0 + defPosition(event).y - y0 + 'px';	
		
		document.getElementById("leftDiv").style.height = 
			document.getElementById("horizontal2").offsetTop - 
			document.getElementById("leftDiv").offsetTop + 'px';
			
		document.getElementById("mainDiv").style.height = document.getElementById("leftDiv").style.height;
		document.getElementById("dragDiv").style.height = document.getElementById("leftDiv").style.height;
			
		document.getElementById("bottomDiv").style.top =
			document.getElementById("horizontal2").offsetTop + 'px';
			
		document.getElementById("bottomDiv").style.height = 
			window.innerHeight - 
			document.getElementById("horizontal2").offsetTop -
			document.getElementById("horizontal2").clientHeight + 'px';	
			
		placeImage(document.getElementById('leftImg'));	
		placeImage(document.getElementById('mainImage'));	
		for (var i = 0; i < 5; i++) placeImage( document.getElementById( "main_000" + (i+1) ) );
		for (var i = 0; i < 5; i++) placeImage( document.getElementById( "sub_000" + (i+1) ) );
	}
}

document.onmousedown = initMove;
document.onmousemove = moveHandler;

// Если клавишу мыши отпустили вне элемента движение должно прекратиться
document.onmouseup = function() {
    moveState = false;
	dragElement = null;
	dragDirection = null;
}