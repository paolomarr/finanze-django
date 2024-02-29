# import django_heroku
from .default import *
import os
import re
from urllib.parse import urlparse

DEBUG = False

ALLOWED_HOSTS = ['paolomarchetti.tk', 'paolomarchetti.my.to', '.localhost', '127.0.0.1']
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECRET_KEY = os.environ['SECRET_KEY']

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

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"