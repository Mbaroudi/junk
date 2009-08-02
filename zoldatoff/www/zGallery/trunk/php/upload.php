<?php

    error_reporting(E_ALL); 

    include('class.upload/class.upload.php');
	include('class.image.php');
	
	$path_to_root = '../'; 
    $path_full = 'img/full/';
    $path_norm = 'img/norm/';
    $path_thumb = 'img/thumb/';
	$path_upload = 'img/upload/';
	
	$norm_size_y = 500;
	$thumb_size_y = 80;
	
	//header('Cache-Control: no-cache, must-revalidate');
	//header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');
	//header('Content-type: application/json');
	
	if ( isset($_REQUEST['filename']) ) {
		
		$handle = new upload($path_to_root . $path_upload . $_REQUEST['filename']);
		
		//Copy full-sized image
		$handle->Process($path_to_root . $path_full);
		$full_src = $path_full . $handle->file_dst_name;
		
		if (! $handle->processed ) echo $handle->error;
		
		//Copy norm-sized image
		$handle->image_resize   = true;
		$handle->image_ratio_x  = true;
		$handle->image_y		= $norm_size_y;
		$handle->Process($path_to_root . $path_norm);
		$norm_src = $path_norm . $handle->file_dst_name;
		
		if (! $handle->processed ) echo $handle->error;
			
		//Copy thumb image
		$handle->image_resize   = true;
		$handle->image_ratio_x  = true;
		$handle->image_y        = $thumb_size_y;
		$handle->Process($path_to_root . $path_thumb);
		$thumb_src = $path_thumb . $handle->file_dst_name;
		
		if (! $handle->processed ) echo $handle->error;
		
		//Insert data in MySQL	
		connect();
	
		$query = "INSERT INTO IMAGES (full_src, norm_src, thumb_src, uploaddate) VALUES ('" . 
				$full_src  . "', '" . $norm_src . "', '" . 
				$thumb_src . "', curdate() 
				)";
		$query_result = mysql_query($query)
			or die ("Could not execute query '$query'." . mysql_error());
			
		$query = "INSERT INTO IMGALBUM VALUES (LAST_INSERT_ID(), -1)";
		$query_result = mysql_query($query)
			or die ("Could not execute query '$query'." . mysql_error());
		
		//Delete original image
		//$handle->clean();
		if (! $handle->processed ) echo $handle->error;
		//echo $handle->log;
		
		$json = new imagefile($thumb_src, $_REQUEST['number'] );
		echo '{"result": ' . json_encode($json) . '}';
	}
	
	if ( isset($_REQUEST['object']) ) {
		switch ($_REQUEST['object']) {
			case 'newimages':
				if ($handle = opendir($path_to_root . $path_upload))
					while (false !== ($file = readdir($handle))) {
						if($file != '.' && $file != '..' && eregi('\.jpg|\.jpeg|\.gif|\.png', $file))
							$json[] = new imagefile($file, "OK");
					}
				closedir($handle);		
				break;
			case 'images':
				$json = new album($_REQUEST['album_id']);
				$json->expand_info();
				break;
			case 'albums':
				$json = new category($_REQUEST['category_id']);
				$json->expand_info();
				break;
			case 'categories':
				$json = new gallery();
				break;
		}
		
		echo '{"objectlist": ' . json_encode($json) . '}';
	}  
	
	if ( isset($_REQUEST['action']) ) {    
		connect();          		
		switch ($_REQUEST['action']) {
			case 'moveimages2albums':
				$query = "DELETE FROM IMGALBUM WHERE img_id = " . $_REQUEST['imageid'] . " AND alb_id = " . $_REQUEST['currentalbumid'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				// no break - it's important!!!
			case 'copyimages2albums':
				$query = "INSERT INTO IMGALBUM VALUES (" . $_REQUEST['imageid'] . ", " . $_REQUEST['albumid'] . ")";
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$json = new image($_REQUEST['imageid']);
				break;
			case 'movealbums2categories':
				$query = "DELETE FROM ALBUMCATEGORY WHERE alb_id = " . $_REQUEST['albumid'] . " AND cat_id = " . $_REQUEST['currentcategoryid'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				// no break - it's important!!!
			case 'copyalbums2categories':
				$query = "INSERT INTO ALBUMCATEGORY VALUES (" . $_REQUEST['albumid'] . ", " . $_REQUEST['categoryid'] . ")";
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$json = new album($_REQUEST['albumid']);
				break;
			case 'updateimage':
				$query = "UPDATE IMAGES SET NAME = '" . $_REQUEST['name'] . "', descr = '" . $_REQUEST['description'] . "' WHERE id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$json = new image($_REQUEST['id']);
				break;
			case 'updatealbum':
				$query = "UPDATE ALBUMS SET NAME = '" . $_REQUEST['name'] . "', descr = '" . $_REQUEST['description'] . "' WHERE id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$json = new album($_REQUEST['id']);
				break;
			case 'updatecategory':
				$query = "UPDATE CATEGORIES SET NAME = '" . $_REQUEST['name'] . "', descr = '" . $_REQUEST['description'] . "' WHERE id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$json = new category($_REQUEST['id']);
				break;
			case 'removeimage':
				$json = new image($_REQUEST['id']);
				$query = "DELETE FROM IMGALBUM WHERE img_id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$query = "DELETE FROM IMAGES WHERE id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				//TODO: remove image file
				break;
			case 'removealbum':
				$json = new album($_REQUEST['id']);
				$query = "DELETE FROM IMGALBUM WHERE alb_id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$query = "DELETE FROM ALBUMCATEGORY WHERE alb_id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$query = "DELETE FROM ALBUMS WHERE id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				break;
			case 'removecategory':
				$json = new category($_REQUEST['id']);
				$query = "DELETE FROM ALBUMCATEGORY WHERE cat_id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				$query = "DELETE FROM CATEGORIES WHERE id = " . $_REQUEST['id'];
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				break;
			case 'newalbum':
				$query = "INSERT INTO ALBUMS (name, descr, image_id) VALUES ('" . 
						$_REQUEST['name'] . "', '" . 
						$_REQUEST['description'] .
						"', -1)";
				$query_result = mysql_query($query) or die ("Could not execute query '$query'." . mysql_error());	
				
				$query = "SELECT LAST_INSERT_ID() as id";
				$query_result = mysql_query($query) or die ("Cannot execute '$query'." . mysql_error());
				if ($row = mysql_fetch_array($query_result)) {
					$lastid = $row['id'];
				}
				
				$query = "INSERT INTO ALBUMCATEGORY VALUES ($lastid, -1)";
				$query_result = mysql_query($query) or die ("Could not execute query '$query'." . mysql_error());
				
				$json = new album($lastid);
				break;
			case 'newcategory':
				$query = "INSERT INTO CATEGORIES (name, descr, image_id) VALUES ('" . 
						$_REQUEST['name'] . "', '" . 
						$_REQUEST['description'] .
						"', -1)";
				$query_result = mysql_query($query)
					or die ("Could not execute query '$query'." . mysql_error());	
				$json = new category(LAST_INSERT_ID());
				break;
			case 'editalbumicon':
				$query = "UPDATE ALBUMS SET image_id = " . $_REQUEST['imageid'] . " WHERE id = " . $_REQUEST['albumid'];
				$query_result = mysql_query($query)
					or die ("Could not execute query '$query'." . mysql_error());	
				mysql_query("COMMIT");
				$json = new album($_REQUEST['albumid']);
				break;
			case 'editcategoryicon':
				$query = "UPDATE CATEGORIES SET image_id = " . $_REQUEST['imageid'] . " WHERE id = " . $_REQUEST['categoryid'];
				$query_result = mysql_query($query)
					or die ("Could not execute query '$query'." . mysql_error());
				mysql_query("COMMIT");	
				$json = new category($_REQUEST['categoryid']);
				break;
		}
		
		echo '{"result": ' . json_encode($json) . '}';
	}
	
?>
