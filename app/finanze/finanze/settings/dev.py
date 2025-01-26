from .default import *

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a83_adv+ds--8kmf5uet+5pxp4)+rddi$5ox_mb6b2bry$e^&j'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
INSTALLED_APPS += [
    'drf_yasg',
]
SWAGGER_SETTINGS = {
   'DEFAULT_INFO': 'finanze.urls.api_info',
}
LOGGING['loggers']['tradinglog']['level'] = 'DEBUG'
LOGGING['loggers']['movimenti']['level'] = 'DEBUG'
LOGGING['loggers']['finanze']['level'] = 'DEBUG'

CORS_ALLOW_ALL_ORIGINS = True
