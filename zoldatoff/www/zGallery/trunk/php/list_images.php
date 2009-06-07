<?php
	class image {
		public $thumb_src = 'img/thumb/00.jpg';
		public $norm_src = 'img/norm/00.jpg';
		public $full_src = 'img/full/00.jpg';
		
		function __construct($img_name) {
			$this->thumb_src = 'img/thumb/' . $img_name;
			$this->norm_src = 'img/norm/' . $img_name;
			$this->full_src = 'img/full/' . $img_name;
		}
	}
	
	//$img = array();
	
    for($i=1;$i<=2;$i++)
		$img[] = new image($i . 'jpg');
		
	echo '{"imagelist": ' . json_encode($img) . '}';
?>