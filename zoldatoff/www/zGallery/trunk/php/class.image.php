<?php

	$db_host = "localhost";
	$db_name = "gallery";
	$db_user = "gallery";
	$db_password = "zaebis";
	
	class imagefile {
		public $filename;
		public $error;
		
		function __construct($name, $err) {
			$this->filename = $name;
			$this->error = $err;
		}
	}

	class image {
		public $name;
		public $description;
		public $imagedate;
		public $thumb_src;
		public $norm_src;
		public $full_src;
		public $bgcolor;
		public $uploaddate;
		
		function __construct($id) {
			$query = "SELECT * FROM IMAGES WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {
				$this->name = $row['name'];
				$this->description = $row['descr'];
				$this->imagedate = $row['img_date'];
				$this->full_src = $row['full_src'];
				$this->norm_src = $row['norm_src'];
				$this->small_src = $row['small_src'];
				$this->bgcolor = $row['bgcolor'];
				$this->uploaddate = $row['uploaddate'];
			}
		}
	}
	
	class album {
		public $name;
		public $description;
		public $image_list;
		
		function __construct($id) {
			$query = "SELECT * FROM ALBUMS WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {	
				$this->name = $row['name'];
				$this->description = $row['descr'];
			}
			
			$query = "SELECT * FROM V_IMGALBUM WHERE alb_id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->image_list[] = new image($row['img_id']);
			}
		}
	}
	
	class category {
		public $name;
		public $description;
		public $album_list;
		
		function __construct($id) {
			$query = "SELECT * FROM CATEGORIES WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {	
				$this->name = $row['name'];
				$this->description = $row['descr'];
			}
			
			$query = "SELECT * FROM V_ALBUMCATEGORY WHERE cat_id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->album_list[] = new album($row['alb_id']);
			}
		}
	}

?>