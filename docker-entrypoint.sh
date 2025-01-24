#!/bin/bash

set -x
# rm -rf app/finanze/staticfiles
python app/finanze/manage.py migrate --skip-checks # || exit 1
# python app/finanze/manage.py compilescss
# if [[ "$DJANGO_SETTINGS_MODULE" =~ production ]]; then
    # python app/finanze/manage.py collectstatic --ignore=*.scss
    # STATIC_OPT="--nostatic"
# fi
# if [[ "$DJANGO_SETTINGS_MODULE" =~ dev ]]; then
#     python app/finanze/manage.py makemessages -a
#     python app/finanze/manage.py compilemessages
# fi
python app/finanze/manage.py runserver ${STATIC_OPT} 0.0.0.0:8000
