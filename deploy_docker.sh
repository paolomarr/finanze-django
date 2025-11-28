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
PROFILE=${PROFILE:-production}

while [[ $# -gt 0 ]]; do
    case "$1" in
    -p|--profile)PROFILE="$2"; shift;;
    *) echo "Unknown argument $1">&2; exit 1;; 
    esac
    shift
done


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

# tag current image, so we can remove it after a successful deployment
export GIT_HASH=`git rev-parse --short HEAD`
docker tag finanzeapp-backend-django:latest finanzeapp-backend-django:$GIT_HASH
docker compose up -d --build && \
    docker rmi finanzeapp-backend-django:$GIT_HASH
