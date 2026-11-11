#!/bin/bash
out="$1"
months="202511 202512 202601 202602 202603 202604 202605 202606 202607 202608 202609 202610"
for node in TH_NP15_GEN-APND TH_SP15_GEN-APND; do
  for m in $months; do
    y=${m:0:4}; mo=${m:4:2}
    a=$(date -j -f "%Y%m%d" "${y}${mo}01" "+%Y%m%d")
    b=$(date -j -v+1m -f "%Y%m%d" "${y}${mo}01" "+%Y%m%d")
    f="$out/${node}_${m}.zip"
    for i in 1 2 3 4; do
      curl -s -f -L -o "$f" "https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=${node}&startdatetime=${a}T08:00-0000&enddatetime=${b}T08:00-0000" && unzip -t -q "$f" >/dev/null 2>&1 && { echo "$f ok"; break; }
      echo "$f retry $i"; sleep 20
    done
    sleep 7
  done
done
