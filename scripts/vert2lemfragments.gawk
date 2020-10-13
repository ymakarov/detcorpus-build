#!/bin/gawk
BEGIN { FS = "\t" ; OFS="\t" ; 
	#print "docid", "fragid", "lem", "text", "names";
	}

$1 ~ /^<doc/ { match($0, /id="([^"]*)"/, meta); docid = meta[1]; next }
$1 ~ /^<f/ { match($0, /id=([0-9]+)/, meta); fragid = meta[1]; next }
$3 ~ /^(c|CONJ|APRO|PR|SPRO|PART)$/ { text = text " " $1 ; next }
$4 ~ /(фам|имя|отч)/ { nwords += 1 ; text = text " " $1 ; names[$2] += 1; next }
NF == 5 { if ($3 != "c" ) { sent = sent " " $2 } ; text = text " " $1 }
$1 == "</f>" { 
    for (n in names) {allnames = allnames n " "}
    printf "%s\t%d\t%s\t%s\t%s\n", docid, fragid, sent, text, allnames
    sent = ""
    text = ""
    allnames = ""
    delete names
}
