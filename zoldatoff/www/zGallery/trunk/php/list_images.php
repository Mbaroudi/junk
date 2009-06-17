<?php
	class image {
		public $thumb_src = 'img/thumb/00.jpg';
		public $norm_src = 'img/norm/00.jpg';
		public $full_src = 'img/full/00.jpg';
		public $number = 0;
		public $title = 'title';
		
		function __construct($img_name, $n) {
			$this->thumb_src = 'img/thumb/' . $img_name;
			$this->norm_src = 'img/norm/' . $img_name;
			$this->full_src = 'img/full/' . $img_name;
			$this->number = $n;
			$this->title = 'Title ' . $n;
		}
	}
	
    for($i=1;$i<=9;$i++)
		$img[] = new image('0' . $i . '.jpg', $i-1);
	
	for($i=10;$i<=25;$i++)
		$img[] = new image($i . '.jpg', $i-1);
		
	echo '{"imagelist": ' . json_encode($img) . '}';
?>