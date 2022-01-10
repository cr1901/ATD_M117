#!/bin/sh

if [ $# -lt 3 ]; then
  echo "$0 [switches] [output_number] [output_val]"
  echo "[output_number] is 1-based, right-to-left"
  exit 1
fi

OUT_IGN1=`expr 7 - $2`
OUT_IGN2=`expr 7 - $OUT_IGN1 - 1`
OUT_POS=`expr 14 + $OUT_IGN1`

grep -E "$1: .{$OUT_IGN1}$3.{$OUT_IGN2}" adt.txt | cut -c1-8,12-13,$OUT_POS
