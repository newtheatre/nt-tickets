DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {    
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'NT_TICKETS_DB',
        'USER' : 'tickets',
        'PASSWORD' : 'Tickets01',
        'HOST' : 'nt-tickets-db.c3pyiadaokxt.eu-west-1.rds.amazonaws.com',
        'PORT' : '5432',
    }
}

BASE_URL = 'ticketing.newtheatre.org.uk'

PUBLIC_CATEGORIES = ['theatre','uncut']

AWS_STORAGE_BUCKET_NAME = "nt-tickets-static"
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
STATICFILES_LOCATION = 'static'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

AWS_S3_SECURE_URLS = False    # Use HTTP instead of HTTPS
AWS_QUERYSTRING_AUTH = False    # Remove auth querystrings from the query

MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

ACTUALLY_SEND_MAIL = True

MAX_DISCLOSURE = 10
