# import django_heroku
from .default import *
import os
import re
from urllib.parse import urlparse

DEBUG = True

ALLOWED_HOSTS = ['.localhost', '127.0.0.1']
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECRET_KEY = 'django-insecure-a83_adv+ds--8kmf5uet+5pxp4)+rddi$5ox_mb6b2bry$e^&j'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
dbhost = 'db'
dbport = 5432
dbuser = 'postgres'
dbpass = 'postgres'
dbname = 'postgres'
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

# MIDDLEWARE += [
#     "whitenoise.middleware.WhiteNoiseMiddleware",
# ]