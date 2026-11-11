#!/bin/bash
cd "$1"
for node in TH_NP15_GEN-APND TH_SP15_GEN-APND; do
  for m in 202605 202607 202608 202610; do
    y=${m:0:4}; mo=${m:4:2}
    a="${y}${mo}01"; mid="${y}${mo}16"; b=$(date -j -v+1m -f "%Y%m%d" "$a" "+%Y%m%d")
    rm -f "${node}_${m}.zip"
    for part in "$a $mid a" "$mid $b b"; do
      set -- $part
      f="${node}_${m}$3.zip"
      for i in 1 2 3; do
        curl -s -f -L -o "$f" "https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=${node}&startdatetime=$1T07:00-0000&enddatetime=$2T07:00-0000" && unzip -l "$f" | grep -q "\.csv" && { echo "$f ok"; break; }
        echo "$f retry $i"; sleep 20
      done
      sleep 7
    done
  done
done
