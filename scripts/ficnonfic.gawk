#!/usr/bin/gawk

$0 ~ /^<doc/ && $0 ~ /nonfiction/ { nonfic = 1 }
$0 ~ /^<doc/ && $0 !~ /nonfiction/ { nonfic = 0 }
mode == "nonfic" && nonfic == 1 { print ; next }
mode == "fic" && nonfic == 0 { print ; next }

