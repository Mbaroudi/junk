$(document).ready(function() {
	$("#centerDiv").setimage("img/23.jpg", "title");
});

(function($) {
	$.fn.setimage = function(imgSrc, imgTitle) {
		$div = $(this).addClass("loadingdiv");

		$img = $("<img/>").attr("src", imgSrc).addClass("centerImage");

		$img.load(function() {
			$i = $(this);
			title = imgTitle;

			$div.removeClass("loadingdiv").append($i);
			$i.fadeIn(1000);

			if (title !== null) {
				console.info("Title is not null");
				// $i.attr("title", title);
				// $div.append("<span>" + title + "</span>");
			}
		});
	};

})(jQuery);
