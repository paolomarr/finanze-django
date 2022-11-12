# import django_heroku
from .default import *
import os
import re
from urllib.parse import urlparse

DEBUG = False

ALLOWED_HOSTS = ['paolomarchetti.tk', '.localhost', '127.0.0.1']

SECRET_KEY = os.environ['SECRET_KEY']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
dbhost = 'localhost'
dbport = 5432
dbuser = django
dbpass = os.environ['DJANGO_FINAZE_DB_PASSWORD']
dbname = 'finanze'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': dbhost,
        'PORT': dbport,
        'NAME': dbname,
        'USER': dbuser,
        'PASSWORD': dbpass,
    }
}

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# Configure Django App for Heroku.
# django_heroku.settings(locals(),
#                        databases=False,
#                        test_runner=False,
#                        staticfiles=True,
#                        allowed_hosts=False,
#                        logging=False,
#                        secret_key=False,
#                        )
