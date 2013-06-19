import os
import re

DIRNAME = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

AUTH_USER_MODEL = 'karma.User'

TIME_ZONE = 'GMT'
LANGUAGE_CODE = 'lt-LT'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = ''
MEDIA_URL = ''

STATIC_ROOT = ''
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'upkarma_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'karma',
    'karma.importer',
    'karma.bot',
)

# let's put it in the container folder and not the project folder itself
IMPORTER_LOG_FILENAME = os.path.join(DIRNAME, '..',
                                     'karma_importer.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters' : {
        'simple': {
            'format' : '%(asctime)s [%(name)s] %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'log_importer': {
            'level' : 'INFO',
            'class' : 'logging.FileHandler',
            'formatter' : 'simple',
            'filename' : IMPORTER_LOG_FILENAME,
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'karma.importer' : {
            'handlers' : ['log_importer'],
            'level' : 'INFO',
        }
    }
}

UPKARMA_SETTINGS = {
    'app_credentials': {
        'consumer_key' : 'dummy',
        'consumer_secret' : 'dummy',
    },
    'global_credentials': {
        'consumer_key' : 'dummy',
        'consumer_secret' : 'dummy',
        'token' : 'dummy',
        'token_secret' : 'dummy',
    },
    're_amount' : re.compile(r'#upkarma\s+(\d)(?!\d)'),
    'limits' : {
        'per_week' : 50,
        'per_week_receiver' : 15
    },
    'valid_amount_range' : (1,5),
    # passed to StrictRedis constructor
    'redis' : {
    }
}

try:
    from local_settings import *
except ImportError:
    raise Exception('Needs local_settings to run')
