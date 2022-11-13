#!/bin/bash

python app/finanze/manage.py compilescss --delete-files
python app/finanze/manage.py collectstatic --ignore=*.scss
python app/finanze/manage.py runserver --nostatic 0.0.0.0:8000
