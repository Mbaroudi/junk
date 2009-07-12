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
	$thumb_size_y = 100;
	
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
		mysql_pconnect($db_host, $db_user, $db_password) 
			or die ("Could not connect to the MySQL server '$db_host' as user '$db_user'." . mysql_error());
		mysql_select_db($db_name) 
			or die ("Could not select DB '$db_name'." . mysql_error());
	
		$query = "INSERT INTO IMAGES (full_src, norm_src, thumb_src, uploaddate) VALUES ('" . 
				$full_src  . "', '" . $norm_src . "', '" . 
				$thumb_src . "', curdate() 
				)";
		$query_result = mysql_query($query)
			or die ("Could not execute query '$query'." . mysql_error());
		
		mysql_close();
	
		//Delete original image
		//$handle->clean();
		if (! $handle->processed ) echo $handle->error;
		//echo $handle->log;
		
		$json = new imagefile($thumb_src, $_REQUEST['number'] );
		echo '{"result": ' . json_encode($json) . '}';
	}
	else { //if(isset($_REQUEST['filename']))      
		if ($handle = opendir($path_to_root . $path_upload))
			while (false !== ($file = readdir($handle))) {
				if($file != '.' && $file != '..' && eregi('\.jpg|\.jpeg|\.gif|\.png', $file))
					$json[] = new imagefile($file, "OK");
			}
		closedir($handle);
		
		echo '{"file_list": ' . json_encode($json) . '}';
	} //if(isset($_REQUEST['filename']))                   		
			
?>
