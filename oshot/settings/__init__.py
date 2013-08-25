from __future__ import absolute_import
import os

if 'HEROKU' in os.environ:
    from .heroku import *
elif 'OPENSHIFT_HOMEDIR' in os.environ:
    from .openshift import *
elif 'NSA' in os.environ:
    from .nsa import *
else:
    from .dev import *

try:
    if SINGLE_PROCESS:
        # TODO: the next line is neccessery because celery-haystck needs to be fixed
        #       https://github.com/jezdez/celery-haystack/issues/21
        HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'
        CELERY_ALWAYS_EAGER = True
except:
    ''' default is a multi process env '''
    from .multi import *

