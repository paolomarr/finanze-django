#!/bin/bash

set -x
rm -rf app/finanze/staticfiles
python app/finanze/manage.py migrate || exit 1
python app/finanze/manage.py compilescss
if [[ "$DJANGO_SETTINGS_MODULE" =~ "dev$" ]]; then
    python app/finanze/manage.py collectstatic --ignore=*.scss
    STATIC_OPT="--nostatic"
fi
python app/finanze/manage.py runserver ${STATIC_OPT} 0.0.0.0:8000