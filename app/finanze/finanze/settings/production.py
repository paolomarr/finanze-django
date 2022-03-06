from .default import *
import os
import re

DEBUG = False

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
ALLOWED_HOSTS = ['.herokuapp.com', '.localhost', '127.0.0.1']

SECRET_KEY = os.environ['SECRET_KEY']
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

dbhost = os.environ['DATABASE_URL']
dbname = re.sub(r'.*\/', '', dbhost)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': dbhost,
        'NAME': dbname,
    }
}
