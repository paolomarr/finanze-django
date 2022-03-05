from .default import *
import os

DEBUG = False

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
ALLOWED_HOSTS = ['.herokuapp.com', '.localhost', '127.0.0.1']

SECRET_KEY = os.environ['SECRET_KEY']
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['DATABASE_URL'],
    }
}
