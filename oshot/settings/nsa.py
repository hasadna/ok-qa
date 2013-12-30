from __future__ import absolute_import

from os import environ
from .base import *
from .s3 import *

ALLOWED_HOSTS = ("oshot.hasadna.org.il", ".localshot.org.il", )
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', False)
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'oshot',                      # Or path to database file if using sqlite3.
        'USER': 'oshot',                      # Not used with sqlite3.
        'PASSWORD': 'oshot',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

ANALYTICS_ID = os.environ.get('ANALYTICS_ID')

ADMINS += [('tbrisker', 'tbrisker@gmail.com') ]
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

