# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import sys
sys.path.insert(0, os.path.dirname(BASE_DIR))

SECRET_KEY = 'pf87b=3sm!abi6dbt3b8b3hw$yqp4^7#f*87&l2r7tr2qx2_@s'
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'testapp',
)

MIDDLEWARE = MIDDLEWARE_CLASSES = (
    'qinspect.middleware.QueryInspectMiddleware',
)

ROOT_URLCONF = 'testproject.urls'
WSGI_APPLICATION = 'testproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

QUERY_INSPECT_ENABLED = True
QUERY_INSPECT_LOG_STATS = True
QUERY_INSPECT_HEADER_STATS = True
QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True
QUERY_INSPECT_TRACEBACK_ROOTS = [BASE_DIR]
QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = 1
QUERY_INSPECT_ABSOLUTE_LIMIT = -1
QUERY_INSPECT_SQL_LOG_LIMIT = 100

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'memory': {
            'level': 'DEBUG',
            'class': 'testapp.memorylog.MemoryHandler',
        },
    },
    'loggers': {
        'qinspect': {
            'handlers': ['memory'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
