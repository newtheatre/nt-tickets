# -*- coding: utf-8 -*-
# All common settings for nt_tickets project.
import os
import configuration.environment as env
import configuration.keys as keys
import raven

def gettext(s):
    return s

PROJECT_PATH = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

MAX_DISCLOSURE = 10

RECAPTCHA_PUBLIC_KEY = keys.RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = keys.RECAPTCHA_PRIVATE_KEY

AWS_S3_HOST = "s3-eu-west-1.amazonaws.com"
AWS_ACCESS_KEY_ID = keys.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = keys.AWS_SECRET_ACCESS_KEY

# Email SES and seacucumber
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'eu-west-1'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'
AWS_SES_ACCESS_KEY_ID = keys.AWS_ACCESS_KEY_ID
AWS_SES_SECRET_ACCESS_KEY = keys.AWS_SECRET_ACCESS_KEY

# Cache
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.chache.backends.locmem.locMemCache',
#         'LOCATION': 'unique-snowflake'
#     }
# }

# The repository to add this issue to
REPO_OWNER = 'newtheatre'
REPO_NAME = 'nt-tickets'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'
DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

STATIC_ROOT = os.path.join(PROJECT_PATH, "static")

# Additional locations of static files
STATICFILES_DIRS = ()

# Change the default serialiser
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '53-33z*96fb&amp;6rcc%(44z7_7hms-3updy(75j#fmwy=mg=1p9@'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            PROJECT_PATH+'/templates',
        ],
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
            'loaders': [
                # insert your TEMPLATE_LOADERS here
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                # 'django.template.loaders.eggs.Loader',
            ]
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'south',
    'mathfilters',
    'admin_reorder',
    'bootstrap_toolkit',
    'storages',
    'stdimage',
    'raven.contrib.django.raven_compat',
    'django_ses',

    'tickets',
    'pricing',

    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
)

# Reording of admin models
# For more info see django-modeladmin-reorder
ADMIN_REORDER = (
    'auth',
    'sites',

    {
    'app': 'tickets',
    'models': (
        'tickets.Category',
        'tickets.Show',
        'tickets.Occurrence',
        'tickets.Ticket',
        )
    },

    {
    'app': 'pricing',
    'models': (
        'pricing.SeasonTicketPricing',
        'pricing.InHousePricing',
        'pricing.FringePricing',
        'pricing.ExternalPricing',
        'pricing.StuFFPricing',
        'pricing.StuFFEventPricing',
        )    
    },
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# What enviroment are we in?
if env.RUN_ENV == 'production':
    from configuration.production import *

    # Only run Raven in production environment
    RAVEN_CONFIG = {
        'dsn': keys.DSN,
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        'release': raven.fetch_git_sha(os.path.dirname(__file__)),
    }
elif env.RUN_ENV == 'staging':
    from configuration.staging import *
elif env.RUN_ENV == 'development':
    from configuration.development import *
elif env.RUN_ENV == 'testing':
    from configuration.testing import *
