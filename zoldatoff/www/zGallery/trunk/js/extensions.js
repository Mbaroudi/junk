/**
 * @author zoldatoff
 */

 jQuery.fn.center = function() {
	var iHeight = $(this).height();	
	var dHeight = $(this).parent().height();
	var iWidth 	= $(this).width();
	var dWidth 	= $(this).parent().width();
	
	var myMargin = 0;
	
	if (dWidth > iWidth && dHeight > iHeight) {
		myMargin = (dHeight - iHeight)/2;
	}
	else if (dWidth/dHeight < iWidth/iHeight) {
		myMargin = (dHeight*iWidth - iHeight*dWidth)/(2*iWidth);
	}
	else {
		myMargin = 0;
	}
	
	$(this).css( 'margin-top', myMargin + 'px' );
}