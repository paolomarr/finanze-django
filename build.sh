#!/bin/bash

base_version=`grep "\"version\":" movimenti-fe/package.json| sed -E 's/[^0-9\.]//g'`
commit=$(git rev-parse --short HEAD || echo "nvc")
date=$(date '+%Y%m%d%H%M%S')
version_info="$commit-$date"
if [[ -n "$base_version" ]]; then
    version_info=${base_version}-${version_info}
fi
docker build -f Dockerfile_react -t finanze-django-react_frontend:${version_info} --build-arg "version_info=$version_info" .