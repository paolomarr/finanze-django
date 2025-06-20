from .default import *
import os

DEBUG = False

ALLOWED_HOSTS = ['paolomarchetti.tk', 'paolomarchetti.my.to', '.localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS.append('https://paolomarchetti.my.to')

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

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"