<?php

	include('class.image.php');

	mysql_pconnect($db_host, $db_user, $db_password) or die ("Could not connect to the MySQL server '$db_host' as user '$db_user'." . mysql_error());
	mysql_select_db($db_name) or die ("Could not select DB '$db_name'." . mysql_error());
		
	$json = new category(0);	
	echo '{"category_list": [' . json_encode($json) . ']}';
	
	mysql_close();

?>