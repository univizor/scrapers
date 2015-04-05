<?php 
	echo "Start";
	
	$base_path = "/mnt/univizor/download";
	
	$table = "docDB";
	$faks = "doba";
	mkdir($base_path."/".$faks);
	
	$mysqli = new mysqli("univizor.cvzapunv5plz.us-east-1.rds.amazonaws.com", "univizor", "univizor9", "univizor");
	$mysqli->query("SET NAMES utf8");
	
	$url = "http://www.doba.si/diplome/14400";

	for($n=0;$n<1000;$n++) {
		$st = $n;
		while(strlen($st)<3) $st = "0".$st;
		
		try {
			$x = @file_get_contents($url.$st.".pdf");
			if (strlen($x)<10000) continue;
		} catch (exception $e) {
			continue;
		}
		$urlf = $url.$st.".pdf"; 
		
		$mysqli->query("insert into {$table} (url,fakulteta) values ('{$urlf}','{$faks}');");
		$id = $mysqli->insert_id;
		
		$filename = $base_path."/".$faks."/".$id.".pdf";
		
		if ($table=="docDB") file_put_contents($filename,$x);
		$mysqli->query("update {$table} set filename='{$filename}' where id={$id};");

		echo $urlf." ".$filename."\n";
	}

	echo "\n\n\n";