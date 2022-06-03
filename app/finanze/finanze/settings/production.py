import django_heroku
from .default import *
import os
import re
from urllib.parse import urlparse

DEBUG = False

ALLOWED_HOSTS = ['.herokuapp.com', '.localhost', '127.0.0.1']

SECRET_KEY = os.environ['SECRET_KEY']
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

dburl = urlparse(os.environ['DATABASE_URL'])
dbhost = dburl.hostname
dbport = dburl.port
dbuser = dburl.username
dbpass = dburl.password
dbname = re.sub(r'^\/', '', dburl.path)
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

# Configure Django App for Heroku.
django_heroku.settings(locals(),
                       databases=False,
                       test_runner=False,
                       staticfiles=True,
                       allowed_hosts=False,
                       logging=False,
                       secret_key=False,
                       )
