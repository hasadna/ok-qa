import os

STATIC_S3 = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = False

STATIC_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = STATIC_URL + 'media/'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
