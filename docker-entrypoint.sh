#!/bin/bash

set -x
# rm -rf app/finanze/staticfiles
python app/finanze/manage.py migrate --skip-checks || exit 1
# static files (admin CSS/JS) for WhiteNoise; .scss sources are not served
python app/finanze/manage.py collectstatic --noinput --ignore='*.scss' -v 0 || exit 1
if [[ "$DEMO_MODE" == "1" ]]; then
    # idempotent: does nothing if the demo user already has data
    python app/finanze/manage.py seed_demo
fi
# python app/finanze/manage.py compilescss
# if [[ "$DJANGO_SETTINGS_MODULE" =~ dev ]]; then
#     python app/finanze/manage.py makemessages -a
#     python app/finanze/manage.py compilemessages
# fi
python app/finanze/manage.py runserver 0.0.0.0:8000
