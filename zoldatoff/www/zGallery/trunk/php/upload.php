<?php

    error_reporting(E_ALL); 

    // we first include the upload class, as we will need it here to deal with the uploaded file
    include('class.upload/class.upload.php');
	include('class.image.php');

    $path_full = '../img/full/';
    $path_norm = '../img/norm/';
    $path_thumb = '../img/thumb/';
	$path_upload = '../img/upload/';
	
	$norm_size_y = 500;
	$thumb_size_y = 150;
	
	if ( isset($_REQUEST['action']) ) {      
	
		if ($_REQUEST['action'] == 'listFiles') {
							
			if ($handle = opendir($path_upload))
				while (false !== ($file = readdir($handle))) {
					if($file != '.' && $file != '..' && eregi('\.jpg|\.jpeg|\.gif|\.png', $file))
						$json[] = new imagefile($file, "OK");
				}
			closedir($handle);
			
			echo '{"file_list": ' . json_encode($json) . '}';
			
		} 
	} //if(isset($_REQUEST['action']))                   		
			
		
	if (isset($_REQUEST['filename']) && isset($_REQUEST['filesize'])){

		$handle = new upload($path_upload."/".$_REQUEST['filename']);
		
		echo '{"result":[';
		
		switch ($_REQUEST['filesize']) {
			case 'full':
				$handle->Process($path_full);
				if ($handle->processed)
					$json = new imagefile($path_full . $handle->file_dst_name, "OK");
				else
					$json = new imagefile($handle->error, "KO");
				break;
			case 'norm':
				$handle->image_resize            = true;
				$handle->image_ratio_x           = true;
				$handle->image_y                 = $norm_size_y;
				$handle->Process($path_norm);
				if ($handle->processed)
					$json = new imagefile($path_norm . $handle->file_dst_name, "OK");
				else
					$json = new imagefile($handle->error, "KO");
				break;
			case 'thumb':
				$handle->image_resize            = true;
				$handle->image_ratio_x           = true;
				$handle->image_y                 = $thumb_size_y;
				$handle->Process($path_thumb);
				if ($handle->processed)
					$json = new imagefile($path_thumb . $handle->file_dst_name, "OK");
				else
					$json = new imagefile($handle->error, "KO");
				break;
			case 'delete':
				$handle->Clean();
				if ($handle)
					$json = new imagefile("success", "OK");
				else
					$json = new imagefile($handle->error, "KO");
				break;
		}
		
		echo '{"result": ' . json_encode($json) . '}';
		
	} //if(isset($_REQUEST['filename']) && isset($_REQUEST['filesize'])
	
	if (isset($_REQUEST['fullname']) 
		&& isset($_REQUEST['normname']) 
		&& isset($_REQUEST['thumbname']) 
		&& isset($_REQUEST['uploaddate'])
		) 
	{
		
		mysql_pconnect($db_host, $db_user, $db_password) or die ("Could not connect to the MySQL server '$db_host' as user '$db_user'." . mysql_error());
		mysql_select_db($db_name) or die ("Could not select DB '$db_name'." . mysql_error());
	
		$query = "INSERT INTO IMAGES (full_src, norm_src, thumb_src, uploaddate) VALUES ('" . 
				$_REQUEST['fullname']  . "', '" . $_REQUEST['normname'] . "', '" . 
				$_REQUEST['thumbname'] . "', '" . $_REQUEST['uploaddate'] . "')";
		$query_result = mysql_query($query);
		
		if (!$query_result)
			$json = new imagefile("SQL query error: ' . mysql_error() . '", "KO");
		else
			$json = new imagefile("SQL executed successfully", "OK"); 
			
		mysql_close();
		
		echo '{"result": ' . json_encode($json) . '}';
		
	} //if (isset($_REQUEST['fullname']) && isset($_REQUEST['normname']) && isset($_REQUEST['thumbname']))

?>
