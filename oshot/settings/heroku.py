from __future__ import absolute_import

import dj_database_url

from os import environ
from .base import *
from .s3 import *

ALLOWED_HOSTS = (".herokuapp.com", )
ENV = 'HEROKU'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', False)
TEMPLATE_DEBUG = DEBUG

DATABASES = { 'default': dj_database_url.config() }

EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST= 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
EMAIL_USE_TLS = True

ANALYTICS_ID = os.environ.get('ANALYTICS_ID')
