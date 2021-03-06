import os
import re

DIRNAME = os.path.dirname(__file__)

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django_postgrespool',
        'NAME': 'upkarma',
        'USER': 'upkarma',
        'PASSWORD': 'hunter2',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

SECRET_KEY = 'insecure-development-secret-key'

MANAGERS = ADMINS

AUTH_USER_MODEL = 'karma.User'
AUTHENTICATION_BACKENDS = ('karma.auth.TwitterBackend',)

TIME_ZONE = 'Europe/Vilnius'
USE_TZ = True

LANGUAGE_CODE = 'lt-LT'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = ''
MEDIA_URL = ''

STATIC_ROOT = os.path.join(DIRNAME, '..', 'static')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'upkarma_project.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    'rest_framework',
    'markdown_deux',

    'karma',
    'karma.importer',
    'karma.bot',
    'karma.stream',
    'karma.news',
)

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # none.
    'DEFAULT_PERMISSION_CLASSES': []
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    },
]

MARKDOWN_DEUX_STYLES = {
    "trusted": {
        # Allow raw HTML (WARNING: don't use this for user-generated
        # Markdown for your site!).
        "safe_mode": False,
    }
}

TEST_RUNNER = 'karma.test_runner.KarmaTestRunner'

# let's put it in the container folder and not the project folder itself
IMPORTER_LOG_FILENAME = os.path.join(DIRNAME, '..', 'karma_importer.log')
BOT_LOG_FILENAME = os.path.join(DIRNAME, '..', 'karma_bot.log')
OTHER_LOG_FILENAME = os.path.join(DIRNAME, '..', 'karma_other.log')
ERROR_LOG_FILENAME = os.path.join(DIRNAME, '..', 'karma_errors.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters' : {
        'simple': {
            'format' : '%(asctime)s [%(name)s] %(message)s'
        }
    },
    'handlers': {
        'log_error': {
            'level' : 'ERROR',
            'class' : 'logging.FileHandler',
            'filters': ['require_debug_false'],
            'filename' : ERROR_LOG_FILENAME,
        },
        'log_importer': {
            'level' : 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter' : 'simple',
            'filename' : IMPORTER_LOG_FILENAME,
        },
        'log_bot' : {
            'level' : 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter' : 'simple',
            'filename' : BOT_LOG_FILENAME,
        },
        'log_other' : {
            'level' : 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter' : 'simple',
            'filename' : OTHER_LOG_FILENAME,
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['log_error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'karma.importer' : {
            'handlers' : ['log_importer'],
            'level' : 'DEBUG',
        },
        'karma.bot' : {
            'handlers' : ['log_bot'],
            'level' : 'DEBUG',
        },
        'karma.other' : {
            'handlers' : ['log_other'],
            'level' : 'DEBUG',
        },
    },
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
    'hashtag' : '#upkarma',
    # the hashtag, followed by one or more whitespace symbols,
    # followed by zero or one plus
    # followed by a digit that is not followed by a digit
    're_amount' : re.compile(r'#upkarma\s+\+?(\d)(?!\d)'),
    'limits' : {
        'per_week' : 50,
        'per_week_receiver' : 15
    },
    'valid_amount_range' : (1,5),
    # passed to StrictRedis constructor
    'redis' : {
    },
    'callback_uri' : 'http://dummy/'
}
