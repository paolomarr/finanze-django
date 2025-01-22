#!/bin/bash

function _stderrecho() {
    echo "$1" >&2
}
function info() {
    _stderrecho "[INFO] $1"
}

function warning() {
    _stderrecho "[WARNING] $1"
}

function error() {
    _stderrecho "[ERROR] $1"
}

function generate_secret_key() {
    if [[ -n `which openssl` ]]; then
        info "Using 'openssl rand' to generate random key..."
        _secret_key=`openssl rand -hex 32`
    else
        if [[ -e /dev/urandom ]]; then
            RAND=/dev/urandom
        elif [[ -e /dev/random ]]; then
            RAND=/dev/random
        fi
        if [[ -n $RAND ]]; then
            info "Using '$RAND + shasum' to generate random key..."
            _secret_key=`cat /dev/urandom | head -c 32 | shasum -a 1| cut -d ' ' -f 1`
        fi
    fi
    if [[ -z "$_secret_key" ]]; then
        error "Unable to generate random SECRET_KEY. Please insert a key manually. Hint: provide a robust, long, random string (at least 32 character long)"
        read -s -p "Your secret key: " _secret_key
        echo
    fi
    echo $_secret_key
}

SCRIPT_ROOT=`cd $(dirname $0); pwd`
MAIN_ENV_FILE=${SCRIPT_ROOT}/app/finanze/.env
FE_ENV_FILE=${SCRIPT_ROOT}/movimenti-fe/.env
PROFILE=${PROFILE:-production}

while [[ $# -gt 0 ]]; do
    case "$1" in
    -p|--profile)PROFILE="$2"; shift;;
    *) echo "Unknown argument $1">&2; exit 1;; 
    esac
    shift
done

base_version=`grep "\"version\":" movimenti-fe/package.json| head -n 1 | sed -E 's/[^0-9\.]//g'`
commit=$(git rev-parse --short HEAD || echo "nvc")
date=$(date '+%Y%m%d%H%M%S')
version_info="$commit-$date"
if [[ -n "$base_version" ]]; then
    version_info=${base_version}-${version_info}
fi

# these exported will filter through the docker compose file
export REACT_FRONTEND_TAG=finanze-django-react_frontend:${version_info}
export VERSION_INFO=${version_info}

if [[ ! -f $MAIN_ENV_FILE ]]; then
    info "Generating .env file for DJANGO runtime environment variables" >&2
    echo 'DJANGO_SETTINGS_MODULE=finanze.settings.production' >> $MAIN_ENV_FILE
    echo "SECRET_KEY=`generate_secret_key`" >> $MAIN_ENV_FILE
    info "If you have a RapidAPI subscription to use with the trading app, insert the RAPIDAPI_KEY here"
    read -p "Insert RAPIDAPI_KEY (leave empty to skip this passage): " -s RAPIDAPI_KEY
    echo
    if [[ -z "$RAPIDAPI_KEY" ]]; then
        info "You chose not to enable the RapidAPI connection. Some of the features of the Tradinglog app will not be available"
        RAPIDAPI_KEY="not_available"
    fi
    echo "RAPIDAPI_KEY=$RAPIDAPI_KEY" >> $MAIN_ENV_FILE
else
    info "$MAIN_ENV_FILE file found"
    for ptn in "SECRET_KEY=" "DJANGO_SETTINGS_MODULE="; do
        found=`grep $ptn $MAIN_ENV_FILE`
        if [[ -z $found ]]; then
            error "The .env file has no $ptn variable defined. This is required, please edit the $MAIN_ENV_FILE file and add it."
            exit 1
        fi
    done
fi
if [[ ! -f $FE_ENV_FILE ]]; then
    info "Generating .env file for REACT runtime environment variables" >&2
    echo 'BACKEND_API_MOVEMENTS_URL="http://localhost:8003/movements"' > $FE_ENV_FILE
    echo 'BACKEND_API_TRADINGLOG_URL="http://localhost:8003/tradinglog"' > $FE_ENV_FILE
    echo 'BACKEND_API_TOKENAUTH_URL="http://localhost:8003/api-token-auth"' > $FE_ENV_FILE
    echo 'BACKEND_API_SCANRECEIPT_URL="http://localhost:8003/scan-receipt"' > $FE_ENV_FILE
    echo "REACT_APP_VERSION_INFO=\"${VERSION_INFO}\"" >> $FE_ENV_FILE
else
    info "$FE_ENV_FILE file found"
    found=`grep REACT_APP_API_URL ${FE_ENV_FILE}`
    if [[ -z $found ]]; then
        error "The .env file has no REACT_APP_API_URL variable defined. This is required, please edit the $FE_ENV_FILE file and add it."
        exit 1
    fi
    found=`grep REACT_APP_VERSION_INFO ${FE_ENV_FILE} | cut -d "=" -f 2`
    if [[ -z $found ]]; then
        info "The .env file has no REACT_APP_VERSION_INFO. Adding it at the end."
        echo "" >> ${FE_ENV_FILE}
        echo "REACT_APP_VERSION_INFO=\"${VERSION_INFO}\"" >> $FE_ENV_FILE
    else
        info "Updating REACT_APP_VERSION_INFO to ${VERSION_INFO} (was $found)"
        sed -i 's/REACT_APP_VERSION_INFO=.*$/REACT_APP_VERSION_INFO='${VERSION_INFO}'/' $FE_ENV_FILE
    fi
fi


docker compose --profile $PROFILE up -d --build
