#!/bin/bash

base_version=`grep "\"version\":" movimenti-fe/package.json| sed -E 's/[^0-9\.]//g'`
commit=$(git rev-parse --short HEAD || echo "nvc")
date=$(date '+%Y%m%d%H%M%S')
version_info="$commit-$date"
if [[ -n "$base_version" ]]; then
    version_info=${base_version}-${version_info}
fi

# these exported will filter through the docker compose file
export REACT_FRONTEND_TAG=finanze-django-react_frontend:${version_info}
export VERSION_INFO=${version_info}
# docker build -f Dockerfile_react -t ${TAG} --build-arg "version_info=$version_info" .
docker compose --profile react --profile pg_db up -d --build