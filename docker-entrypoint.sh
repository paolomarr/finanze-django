#!/bin/bash

rm -rf app/finanze/staticfiles
python app/finanze/manage.py compilescss
python app/finanze/manage.py collectstatic --ignore=*.scss
python app/finanze/manage.py runserver --nostatic 0.0.0.0:8000
