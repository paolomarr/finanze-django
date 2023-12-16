#!/bin/bash

REFDB="db.sqlite"

posidx=0
function parsepositional() {
    case posidx in
    0) SQLDATA="$1";;
    *) echo "invalid argument" >&2; return -1;;
    esac
    let "posidx += 1"
    return 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
    -r) REFDB="$2"; shif;;
    -*) echo "unknown option"; exit 1;;
    *) parsepositional "$1"; [[ $? -eq 0 ]] || exit 1;;
    esac
    shift
done

if [[ ! -f $REFDB ]]; then
    echo "Invalid REFDB file $REFDB"
    exit 1
fi
if [[ ! -f $SQLDATA ]]; then
    echo "Invalid SQLDATA file $SQLDATA"
    exit 1
fi
sqlite3 $REFDB .schema > schema.sql

rm -rf temp.sqlite
sqlite3 temp.sqlite < schema.sql
sqlite3 temp.sqlite < $SQLDATA


OUTPUT=${REFDB%.sql}.sqlite.sql
echo "BEGIN;" > $OUTPUT
cat $REFDB | sed -e 's/public\.//g' -e 's/true/1/g' -e 's/false/0/g' \
    | grep -E -v "^SET" | grep -v "SELECT pg_catalog.set" >> $OUTPUT

echo "END;" >> $OUTPUT

