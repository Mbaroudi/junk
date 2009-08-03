<?php

	$db_host = "localhost";
	$db_name = "gallery";
	$db_user = "gallery";
	$db_password = "zaebis";
	
	function connect() {
		global $db_host;
		global $db_name;
		global $db_user;
		global $db_password;
		
		mysql_pconnect($db_host, $db_user, $db_password) 
			or die ("Could not connect to the MySQL server '$db_host' as user '$db_user'." . mysql_error());
		mysql_select_db($db_name) 
			or die ("Could not select DB '$db_name'." . mysql_error());
	}
	
	function returnError($errorMessage) {
		die('{"result": {"error":"' . $errorMessage . '"}}');
	}
	
	class imagefile {
		public $filename;
		public $number;
		
		function __construct($name, $num) {
			$this->filename = $name;
			$this->number = $num;
		}
	}

	class image {
		public $image_id;
		public $name;
		public $description;
		public $imagedate;
		public $thumb_src;
		public $norm_src;
		public $full_src;
		public $bgcolor;
		public $uploaddate;
		
		function __construct($id) {
			connect();			
			$query = "SELECT * FROM IMAGES WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {
				$this->image_id = $row['id'];
				$this->name = $row['name'];
				$this->description = $row['descr'];
				$this->imagedate = $row['img_date'];
				$this->full_src = $row['full_src'];
				$this->norm_src = $row['norm_src'];
				$this->thumb_src = $row['thumb_src'];
				$this->bgcolor = $row['bgcolor'];
				$this->uploaddate = $row['uploaddate'];
			}
		}
	}
	
	class album {
		public $album_id;
		public $name;
		public $description;
		public $image_list;
		public $image;
		
		function __construct($id) {
			connect();
			$query = "SELECT * FROM ALBUMS WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {	
				$this->album_id = $row['id'];
				$this->name = $row['name'];
				$this->description = $row['descr'];
				$this->image = new image($row['image_id']);
			}
		}
		
		function expand_info() {
			connect();
			$query = "SELECT * FROM V_IMGALBUM WHERE alb_id = $this->album_id ORDER BY img_id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->image_list[] = new image($row['img_id']);
			}
		}
	}
	
	class category {
		public $category_id;
		public $name;
		public $description;
		public $album_list;
		public $image;
		
		function __construct($id) {
			connect();
			$query = "SELECT * FROM CATEGORIES WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {	
				$this->category_id = $row['id'];
				$this->name = $row['name'];
				$this->description = $row['descr'];
				$this->image = new image($row['image_id']);
			}
		}
		
		public function expand_info() {
			connect();
			$query = "SELECT * FROM V_ALBUMCATEGORY WHERE cat_id = $this->category_id ORDER BY alb_id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->album_list[] = new album($row['alb_id']);
			}
		}
		
	}
	
	class gallery {
		public $category_list;
		
		function __construct() {
			connect();
			$query = "SELECT * FROM CATEGORIES ORDER BY id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->category_list[] = new category($row['id']);
			}
		}
	}

?>