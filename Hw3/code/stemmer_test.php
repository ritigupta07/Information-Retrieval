<?php
namespace cpollett\test_composer;

use seekquarry\yioop\library\PhraseParser;
use seekquarry\yioop\library\FetchUrl;
use seekquarry\yioop\library\CrawlConstants;
use seekquarry\yioop\library\processors\HtmlProcessor;

require_once "vendor/autoload.php";

//define("seekquarry\\yioop\\configs\\DEBUG_LEVEL", 7);
define("seekquarry\\yioop\\configs\\PROFILE", true);

//instantiating PhraseParser loads Utility.php and LocaleFunctions.php needed
$parser = new PhraseParser();


//read the file and collect urls
$file = fopen($argv[1], "r") or exit("Unable to open file!");
$urlArr = array(array());
$i = 0;
while(!feof($file))
{
		$line = fgets($file);
		$urlArr[$i][CrawlConstants::URL] = trim($line); 
		$i = $i + 1;
}
fclose($file);
array_pop($urlArr);

//download the urls
$page_info = FetchUrl::getPages($urlArr);

$htmlProcessor = new HtmlProcessor([], 20000, CrawlConstants::CENTROID_SUMMARIZER);

//build inverted index
//array of term => (docList, freq, postingList)
$invertedIndex = array();
for ($docId = 0; $docId < count($urlArr); $docId++) {
 
		//text extraction from html documents
		$htmlProcessInfo = $htmlProcessor->process($page_info[$docId][CrawlConstants::PAGE], $urlArr[$docId][CrawlConstants::URL]);
		$text = $htmlProcessInfo[CrawlConstants::DESCRIPTION];

		//split the document into terms
        $s = preg_replace("/[^a-zA-Z 0-9]+/", " ", $text);

		//change to lower case
        $toLowerCase = strtolower($s);

		$_term = array();

		//stem the terms if option given
		if($argv[2] == "true") {
			$_term = PhraseParser::stemTerms($toLowerCase, $htmlProcessInfo[CrawlConstants::LANG]);
		} else {
        	$_term = explode(" ", $toLowerCase);
		}

		$index = 0;
		for ($pos = 0; $pos < sizeof($_term); $pos++) {
			if($_term[$pos] == '') {continue;}
			if($_term[$pos] == ' ') {continue;}
			$index++;
			if (array_key_exists($_term[$pos], $invertedIndex)) {
				if (!array_key_exists($docId+1, $invertedIndex[$_term[$pos]]["docList"])) {
					array_push($invertedIndex[$_term[$pos]]["docList"],$docId+1);
				}
				$invertedIndex[$_term[$pos]]["freq"] = $invertedIndex[$_term[$pos]]["freq"] + 1;
				array_push($invertedIndex[$_term[$pos]]["postingList"],[$docId+1,$index]);
			} else {
				$invertedIndex[$_term[$pos]] = array();
				$invertedIndex[$_term[$pos]]["docList"] = array();
				$invertedIndex[$_term[$pos]]["docList"][0] = $docId+1;
				$invertedIndex[$_term[$pos]]["freq"] = 1;
				$invertedIndex[$_term[$pos]]["postingList"] = array();
				$invertedIndex[$_term[$pos]]["postingList"][0] = [$docId+1,$index];
			}
		}
}

//sort and print the inverted index
ksort($invertedIndex);
foreach ($invertedIndex as $key => $value) {
		echo $key;
		echo "\n";
		$docCount = count($invertedIndex[$key]["docList"]);
		echo $docCount;
		echo ",";
		echo $invertedIndex[$key]["freq"];
		foreach($invertedIndex[$key]["postingList"] as $posting) {
				echo ",";
				echo "(";
				echo $posting[0];
				echo ",";
				echo $posting[1];
				echo ")";
		}
		echo "\n";
}
