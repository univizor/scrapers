<?php 
	echo "Start";
	
	$base_path = "/mnt/univizor/download";
	
	$table = "docDB";

	$mysqli = new mysqli("univizor.cvzapunv5plz.us-east-1.rds.amazonaws.com", "univizor", "univizor9", "univizor");
	$mysqli->query("SET NAMES utf8");
	
	$urls = array("http://www.digitalna-knjiznica.bf.uni-lj.si/krajinska-arhitektura.htm");
	foreach($urls as $u) {
		
		$x = file_get_contents($u);
		$x = iconv("WINDOWS-1250","utf8",$x);
		
		$faks = 'BF';
		mkdir($base_path."/".$faks);
		
		
		preg_match_all("/<tr>(.*)<\\/tr>/Uis",$x,$ar);
		foreach($ar[1] as $row) {
			preg_match_all("/<td[^>]*>(.*)<\\/td>/Uis",$row,$ar2);
	
			$avtor = trim(strip_tags(trim($ar2[1][0])));
			$mentor = trim(strip_tags($ar2[1][1]));
			$naslov = trim(strip_tags($ar2[1][2]));
			$year = trim(strip_tags($ar2[1][3]));
			$url = $ar2[1][4];
			
			// var_dump($ar2);
			// echo $url;
			
			if (preg_match('/href="(.*)"/Uis',$url,$ar3)) {
				$url = $ar3[1];
			}
			
			echo $u.",".$avtor.",".$naslov.",".$year.",".$url."\n";
			$data = new stdClass();
			$data->mentor = $mentor;
			$data = json_encode($data);
			try {
				$file = true;
				if ($table=="docDB") $file = file_get_contents($url);
			} catch(Exception $err) {
				$file = false;
			} 
			
			if ($file) {
				$mysqli->query("insert into {$table} (url,naslov,fakulteta,leto,avtor,data) values ('{$url}','{$naslov}','{$faks}','{$year}','{$avtor}','{$data}');");
				$id = $mysqli->insert_id;
				
				$filename = $base_path."/".$faks."/".$id.".pdf";
				
				if ($table=="docDB") file_put_contents($filename,$file);
				$mysqli->query("update {$table} set filename='{$filename}' where id={$id};");
			}	
		}
	}	
	
//	var_dump($ar);
	// echo $x;
	
	echo "\n\n\n";