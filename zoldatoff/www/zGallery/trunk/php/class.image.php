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
	
	class imagefile {
		public $filename;
		public $number;
		
		function __construct($name, $num) {
			$this->filename = $name;
			$this->number = $num;
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
			connect();			
			$query = "SELECT * FROM IMAGES WHERE id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {
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
		public $name;
		public $description;
		public $image_list;
		public $image_src;
		
		function __construct($id) {
			connect();
			$query = "SELECT a.*, i.thumb_src FROM ALBUMS a LEFT JOIN IMAGES i on a.image_id = i.id WHERE a.id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {	
				$this->name = $row['name'];
				$this->description = $row['descr'];
				$this->image_src = $row['thumb_src'];
			}
			
			$query = "SELECT * FROM V_IMGALBUM WHERE alb_id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->image_list[] = $row['img_id'];
			}
		}
	}
	
	class category {
		public $name;
		public $description;
		public $album_list;
		public $image_src;
		
		function __construct($id) {
			connect();
			$query = "SELECT c.*, i.thumb_src FROM CATEGORIES c LEFT JOIN IMAGES i on c.image_id = i.id WHERE c.id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			if ($row = mysql_fetch_array($query_result)) {	
				$this->name = $row['name'];
				$this->description = $row['descr'];
				$this->image_src = $row['thumb_src'];
			}
			
			$query = "SELECT * FROM V_ALBUMCATEGORY WHERE cat_id = $id";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->album_list[] = $row['alb_id'];
			}
		}
		
	}
	
	class gallery {
		public $category_list;
		public $image_src;
		
		function __construct() {
			connect();
			$query = "SELECT c.*, i.thumb_src FROM CATEGORIES c LEFT JOIN IMAGES i on c.image_id = i.id ORDER BY c.ID";
			$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
			while($row = mysql_fetch_array($query_result)) {
				$this->category_list[] = $row['id'];
				$this->image_src = $row['thumb_src'];
			}
		}
	}

?>