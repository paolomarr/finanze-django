#!/bin/bash

python app/finanze/manage.py compilescss
python app/finanze/manage.py runserver --nostatic 0.0.0.0:8000
