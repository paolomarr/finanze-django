#!/bin/bash

INPUT="$1"

if [[ ! -f $INPUT ]]; then
    echo "Invalid input file"
    exit 1
fi

OUTPUT=${INPUT%.sql}.sqlite.sql
echo "BEGIN;" > $OUTPUT
cat $INPUT | sed -e 's/public\.//g' -e 's/true/1/g' -e 's/false/0/g' \
    | grep -E -v "^SET" | grep -v "SELECT pg_catalog.set" >> $OUTPUT

echo "END;" >> $OUTPUT

