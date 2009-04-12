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

var mainDivPadding = 15;
var thumbDivPadding = 5;

document.onmousedown = initMove;
document.onmousemove = moveHandler;

// Если клавишу мыши отпустили вне элемента движение должно прекратиться
document.onmouseup = function() {
    moveState = false;
	dragElement = null;
	dragDirection = null;
}

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
		positionElements();
		positionImages();
    }
	
	if (moveState &&
		dragElement.id == "horizontal2")
	{
		dragElement.style.top = divY0 + defPosition(event).y - y0 + 'px';	
		positionElements();	
		positionImages();
	}
}

function positionElements() {
	var maxX = window.innerWidth;
			var maxY = window.innerHeight;
			
			var leftDiv = document.getElementById("leftDiv");
			var mainDiv = document.getElementById("mainDiv");
			var bottomDiv = document.getElementById("bottomDiv");
			var dragDiv = document.getElementById("dragDiv");
			var hor1Div = document.getElementById("horizontal1");
			var hor2Div = document.getElementById("horizontal2");
			
			dragDiv.style.height = hor2Div.offsetTop  - dragDiv.offsetTop + 'px';
			hor1Div.style.top = dragDiv.offsetTop - hor1Div.offsetHeight + 'px';
			
			with (leftDiv.style) {
				top = dragDiv.offsetTop + 'px';
				width = dragDiv.offsetLeft - 2 + 'px';
				height = hor2Div.offsetTop  - dragDiv.offsetTop - 2 + 'px';
				padding = "0px";
			}
			
			with (mainDiv.style) {
				padding = mainDivPadding + 'px';
				left = dragDiv.offsetLeft + dragDiv.offsetWidth + 'px';
				top = dragDiv.offsetTop + 'px';
				width = maxX - parseInt(left) - 2*mainDivPadding - 2 + 'px';
				height = hor2Div.offsetTop  - dragDiv.offsetTop - 2*mainDivPadding - 2 + 'px';
			}
			
			with (bottomDiv.style) {
				top = hor2Div.offsetTop + hor2Div.offsetHeight + 'px';
				height = maxY - parseInt(top) - 2 + 'px';
				width = maxX - 2 + 'px';
			}
			
			for (var i = 0; i < 5; i++) {
				with (document.getElementById("bottomDiv_000" + (i + 1)).style) {
					padding = thumbDivPadding + 'px';
					height = bottomDiv.offsetHeight - 2 * thumbDivPadding - 2 - 2 + 'px';
				}
			}
}

function positionImages(){
		placeImage(document.getElementById('leftImg'));	
		placeImage(document.getElementById('mainImage'));	
		for (var i = 0; i < 5; i++) placeImage( document.getElementById( "main_000" + (i+1) ) );
		for (var i = 0; i < 5; i++) placeImage( document.getElementById( "sub_000" + (i+1) ) );
}
