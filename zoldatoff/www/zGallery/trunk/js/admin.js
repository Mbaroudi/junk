$(document).ready(function(){
	$.getJSON('php/get.php', {category: '0'}, getCategory);
})

function getCategory(data){
	var myHtml = '';
	for (var i1=0; i1<data.category_list.length; i1++) {
		myHtml += '<tr><td id="tdc">+</td><td>' + data.category_list[i1].name + '</td><td></td><td></td></tr>';
		for (var i2=0; i2<data.category_list[i1].album_list.length; i2++) {
			myHtml += '<tr><td id="tda">+</td><td></td><td>' + data.category_list[i1].album_list[i2].name + '</td><td></td></tr>';
			for (var i3=0; i3<data.category_list[i1].album_list[i2].image_list.length; i3++) {
				myHtml += '<tr><td  id="tdi">+</td><td></td><td></td><td>' + data.category_list[i1].album_list[i2].image_list[i3].name + '</td></tr>';
			}	
		}
	}
	
	$('#theTable').html(myHtml);
	
	$('#tdc').click(function(){
		$('#tda').hide();
		$('#tdi').toggle();
	})
	
	$('#tda').click(function(){
		$('#tdi').toggle();
	})
	
	
	
}