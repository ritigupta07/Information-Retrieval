<?php
namespace cpollett\test_composer;
use seekquarry\yioop\configs as SYC;
use seekquarry\yioop\library as SYL;
use seekquarry\yioop\library\PhraseParser;
require_once "vendor/autoload.php";


$stemmed = PhraseParser::stemTerms($argv[1],'en-US');

foreach ($stemmed as $t) {
    echo $t;
    echo " ";
}

echo "\n";
