for s in `seq 12 18`; do
  echo "$s 0,0,0:"
  grep "^0,0,0" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 0,0,1:"
  grep "^1,0,0" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 0,1,0:"
  grep "^0,1,0" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 0,1,1:"
  grep "^1,1,0" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 1,0,0:"
  grep "^0,0,1" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 1,0,1:"
  grep "^1,0,1" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 1,1,0:"
  grep "^0,1,1" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
  echo "$s 1,1,1"
  grep "^1,1,1" adt.csv | cut -d',' -f$s | tr --delete '\n'
  echo ""
done
