<?php

    error_reporting(E_ALL); 

    // we first include the upload class, as we will need it here to deal with the uploaded file
    include('class.upload/class.upload.php');

    $path_full = 'img/full/';
    $path_normal = 'img/normal/';
    $path_small = 'img/small/';
	$path_upload = 'img/upload/';
	
	$normal_size_y = 500;
	$small_size_y = 150;
	
	$db_address = "localhost";
	$db_name = "gallery";
	$db_user = "gallery";
	$db_password = "zaebis";
	
	if ( isset($_REQUEST['action']) ) {      
	
		if ($_REQUEST['action'] == 'listFiles') {
			echo '{"filelist": [';
				
			if ($handle = opendir($path_upload))
				while (false !== ($file = readdir($handle))) {
					if($file != '.' && $file != '..' && eregi('\.jpg|\.jpeg|\.gif|\.png', $file))
						echo '{"filename":"'.$file.'"},';
				}
			closedir($handle);
			
			echo '{} ]}';
			
		} 
	} //if(isset($_REQUEST['action']))                   		
			
		
	if (isset($_REQUEST['filename']) && isset($_REQUEST['filesize'])){
		//$handle = new Upload($_FILES['filename']);
		$handle = new upload($path_upload."/".$_REQUEST['filename']);
		
		echo '{"result":[';
		
		switch ($_REQUEST['filesize']) {
			case 'full':
				$handle->Process($path_full);
				if ($handle->processed)
					echo '{"error":"OK", "data":"' . $path_full . $handle->file_dst_name . '"}';
				else
					echo '{"error":"KO", "data":"' . $handle->error . '"}';
				break;
			case 'normal':
				$handle->image_resize            = true;
				$handle->image_ratio_x           = true;
				$handle->image_y                 = $normal_size_y;
				$handle->Process($path_normal);
				if ($handle->processed)
					echo '{"error":"OK", "data":"' . $path_normal . $handle->file_dst_name . '"}';
				else
					echo '{"error":"KO", "data":"' . $handle->error . '"}';
				break;
			case 'small':
				$handle->image_resize            = true;
				$handle->image_ratio_x           = true;
				$handle->image_y                 = $small_size_y;
				$handle->Process($path_small);
				if ($handle->processed)
					echo '{"error":"OK", "data":"' . $path_small . $handle->file_dst_name . '"}';
				else
					echo '{"error":"KO", "data":"' . $handle->error . '"}';
				break;
			case 'delete':
				$handle->Clean();
				if ($handle)
					echo '{"error":"OK", "data":"success"}';
				else
					echo '{"error":"KO", "data":"' . $handle->error . '"}';
				break;
		}
		
		echo ']}';
		
	} //if(isset($_REQUEST['filename']) && isset($_REQUEST['filesize'])
	
	if (isset($_REQUEST['fullname']) 
		&& isset($_REQUEST['normname']) 
		&& isset($_REQUEST['smallname']) 
		&& isset($_REQUEST['uploaddate'])
		) 
	{
		echo '{"result":[';
		
		$conn = mysql_pconnect($db_address, $db_user, $db_password);
		if (!$conn)
			echo '{"error":"KO", "data":"MySQL connection error: ' . mysql_error() . '"}';
		elseif (!mysql_select_db($db_name, $conn))
			echo '{"error":"KO", "data":"DB selection error: ' . mysql_error() . '"}';
		else {
			$query = "INSERT INTO IMAGES (full_name, norm_name, small_name, uploaddate) VALUES ('" . 
					$_REQUEST['fullname']  . "', '" . $_REQUEST['normname'] . "', '" . 
					$_REQUEST['smallname'] . "', '" . $_REQUEST['uploaddate'] . "')";
			$query_result = mysql_query($query);
			
			if (!$query_result) 
				echo '{"error":"KO", "data":"SQL query error: ' . mysql_error() . '"}';
			else 
				echo '{"error":"OK", "data":"SQL executed successfully"}';
				
			mysql_query("COMMIT");
			mysql_close($conn);
		}
		
		echo ']}';
		
	} //if (isset($_REQUEST['full_name']) && isset($_REQUEST['norm_name']) && isset($_REQUEST['small_name']))

?>
