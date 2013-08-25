import djcelery

djcelery.setup_loader()
HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

