#!/bin/bash

DATE=`date "+%Y%m%d"`
OUTPUT=/tmp/finanze_db.$DATE.sql

docker exec -it finanze-django-db-1 pg_dump --data-only --inserts --column-inserts -U postgres postgres > $OUTPUT

echo $OUTPUT >&2

