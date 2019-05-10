"""
Django settings for NT_Tickets project.
"""

import os

BASE_URL = 'ticketing.newtheatre.org.uk'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Change the default serialiser
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG'))) if os.environ.get('DEBUG') else True
STAGING = bool(int(os.environ.get('STAGING'))) if os.environ.get('STAGING') else False

# SECURITY WARNING: keep the secret key used in production secret!
if not DEBUG:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
else:
    SECRET_KEY = 'wi$7j2y_g(x_3et3wl*d0kawd1ud3zbncs7^4s(-!!k+20-lsi'

ALLOWED_HOSTS = ['ticketing.newtheatre.org.uk', 'nt-tickets.herokuapp.com']

if DEBUG:
    ALLOWED_HOSTS.append('localhost')

ADMINS = (
    # (Harry Bridge, 'harry@harrybridge.co.uk')
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Redirect all http requests to https

# Email SES and seacucumber
EMAIL_USE_SSL = True
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = bool(int(os.environ.get('EMAIL_USE_TLS', 0)))
    EMAIL_USE_SSL = bool(int(os.environ.get('EMAIL_USE_SSL', 0)))
    DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_FROM')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACTUALLY_SEND_MAIL = True if not DEBUG else False

# The repository to add issues to
REPO_OWNER = 'newtheatre'
REPO_NAME = 'nt-tickets'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'admin_reorder',
    'bootstrap_toolkit',
    'storages',
    'stdimage',
    'raven.contrib.django.raven_compat',
    # 'django_ses',
    # 'debug_toolbar',
    'corsheaders',

    'tickets',
    'pricing',
]

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

CORS_ORIGIN_WHITELIST = [
    "localhost:4000",
    "samosborne.me",
    "newtheatre.org.uk",
    "alpha.newtheatre.org.uk"
]

CORS_URLS_REGEX = r'^/api/.*$'

ROOT_URLCONF = 'NT_Tickets.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR+'/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'NT_Tickets.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

if not DEBUG:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config()

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1

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
        'tickets.Sale',
        'tickets.Warnings',
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

#  Logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
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
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')



# Media files (user uploads)
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Stored on S3 in production
if not (DEBUG or STAGING):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    if os.environ.get('AWS_S3_CUSTOM_DOMAIN'):
        AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_REGION_NAME = 'eu-west-1'
    AWS_S3_SIGNATURE_VERSION = 's3v4'

# Only run Raven in production environment
if not (DEBUG or STAGING):
    RAVEN_CONFIG = {
        'dsn': os.environ.get('DSN'),
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        # 'release': raven.fetch_git_sha(os.path.dirname(__file__)),
    }
